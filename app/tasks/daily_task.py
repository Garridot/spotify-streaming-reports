from app.tasks.user_sync_service import CreateUserStats 
from app.repositories.user_repository import UserRepository
from flask import current_app
from app.core.database import db
from datetime import datetime, timedelta, timezone, time
import logging
import json
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def sync_all_users_daily_register():
    """Task to synchronize the retrieval and storage of all user stats"""
    users_repo = UserRepository(db.session).get_all_user()     
    daily_register_repository = current_app.container.daily_register_repository  

    # Retrieve localtime
    local_time = datetime.now().astimezone()    
    # Convert localtime to UTC
    date = local_time.astimezone(timezone.utc)  

    for user in users_repo:       
        
        get_user_stats = CreateUserStats(user.id)    

        date_limit= datetime.combine(date.date(), time(0, 0, 0, tzinfo=timezone.utc))                
        after_timestamp = int(date_limit.timestamp() * 1000)    

        # Try to retrieve the daily register of today for the user
        daily_registered = daily_register_repository.retrieve_day_register(
            user_id = user.id,                
            date = date.date()
        ) 
        
        if daily_registered is None:
            # If daily_registered is None, it retrieves and creates the daily register for the user
            try:
                date_limit= datetime.combine(date.date(), time(0, 0, 0, tzinfo=timezone.utc))                
                after_timestamp = int(date_limit.timestamp() * 1000)       

                # Request spotify and retrieve the tracks played by the user for the day                      
                sp_res = get_user_stats._get_user_tracks(after_timestamp=after_timestamp)  

                if sp_res is None: 
                    # If sp_res is None, it means that the user has not played any tracks for the time requested
                    return logging.info(f"Not found tracks played on {date.date()} {date.time().replace(microsecond=0)} by user {user.id}") 

                daily_register_repository.add_or_update_daily_register(
                    user_id = user.id,
                    tracks = json.loads(sp_res),                  
                    date = date.date()
                )
                return logging.info(f"Success in retrieving and saving the played tracks on {date.date()} {date.time().replace(microsecond=0)}:00 by the user {user.id}")
            except Exception as e:
                logging.error(f"An error occurred while attempting to store tracks played on {date.date()} {date.time().replace(microsecond=0)}:00 by user {user.id}: {str(e)}")                     

        else:
            # If daily_registered exists, it retrieves the tracks not recorded and updates the daily register for the user

            # Get the date of the last stored "played_at" to determine when to request data from Spotify
            after_timestamp = int(daily_registered.tracks[0]["played_at"])             

            # Request spotify and retrieve the tracks played by the user for the day
            sp_res = get_user_stats._get_user_tracks(after_timestamp=after_timestamp)             

            if sp_res is None: 
                # If sp_res is None, it means that the user has not played any tracks for the time requested
                return logging.info(f"Not found tracks played on {date.date()} {date.time().replace(microsecond=0)}:00 by user {user.id}") 

            try:            
                # create a dataframe that contains the response data from spotify
                sp_res_df = pd.DataFrame(json.loads(sp_res))  

                # Retrieve tracks recorded  
                tracks_recorded = pd.DataFrame(daily_registered.tracks)  

                # Group tracks recorded by artist_normalized, artist_id
                grouped_artists_recorded = tracks_recorded.groupby(['artist_normalized', 'artist_id'])

                # Create a DataFrame to display the necessary data of the artists already recorded
                artists_recorded_df = pd.DataFrame({
                    'artist_name': grouped_artists_recorded['artist_name'].first(),
                    'artist_id': grouped_artists_recorded['artist_id'].first(),  
                    "artist_image": grouped_artists_recorded['artist_image'].first(),   
                    "genres": grouped_artists_recorded["genres"].first(),
                }) 

                # Group the spotify response by artist_normalized, artist_id
                grouped_sp_artists = sp_res_df.groupby(['artist_normalized', 'artist_id']) 

                # Create a DataFrame to display the artists' necessary data retrieved from Spotify tracks.
                artists_of_sp_res_df = pd.DataFrame({
                    'artist_name': grouped_sp_artists['artist_name'].first(),
                    'artist_id': grouped_sp_artists['artist_id'].first(),                       
                })
                
                # Create a DataFrame merging the artists_recorded_df and artists_of_sp_res_df dataframes 
                artists_df = pd.merge(
                    artists_recorded_df,
                    artists_of_sp_res_df,
                    on='artist_name',
                    how='left',
                )

                artists_df = artists_df.rename(columns={'artist_id_x': 'artist_id'})
                artists_df = artists_df.drop(columns=['artist_id_y'])            

                
                # Filter the IDs of artists from the dataframe of the artists recorded 
                recorded_IDs = {artist["artist_id"] for artist in json.loads(artists_recorded_df.to_json(orient="records"))}

                # Filter artists from artists_of_sp_res_df dataframe that are not recorded in the artists_recorded_df dataframe
                not_recorded_artists = [artist for artist in json.loads(artists_of_sp_res_df.to_json(orient="records")) if artist["artist_id"] not in recorded_IDs]
                
                # Request to Spotify API for retrieve the information about the artists not recorded.
                artists_res = get_user_stats.sp_sync_functions._get_artists_played(not_recorded_artists)                     

                # Convert artists_res (json) into a dataframe
                artists_sp_res_df = pd.DataFrame(artists_res)                 

                if artists_sp_res_df.empty:
                    # if artists_sp_res_df is empty, it means that all artists are recorded and it was not necessary to request from Spotify, 
                    # so it uses artists_df dataframe
                    full_artists_data_df = artists_df

                else:                     
                    artists_sp_res_df = artists_sp_res_df.rename(columns={'artist': 'artist_name'})

                    # Create a DataFrame by concatenating the "artists_df" and "artists_sp_res_df" dataframes, 
                    # obtaining the artist data of the new tracks and of the tracks already recorded  
                    full_artists_data_df = pd.concat([artists_df, artists_sp_res_df], ignore_index=True)                

                sp_res_df['artist_name'] = sp_res_df['artist_name'].str.title()
                full_artists_data_df['artist_name'] = full_artists_data_df['artist_name'].str.title()

                # Perform a left merge
                new_tracks_played_data_df = pd.merge(
                    sp_res_df,
                    full_artists_data_df,
                    on='artist_name',
                    how='left',
                suffixes=('', '_from_artists')
                )

                # Combine the artist id columns: prioritize the existing value in df songs, and if it's None, use the one in df_artists
                new_tracks_played_data_df['artist_id'] = new_tracks_played_data_df['artist_id'].fillna(new_tracks_played_data_df['artist_id_from_artists'])

                # Delete the created temporary column
                new_tracks_played_data_df = new_tracks_played_data_df.drop(columns=['artist_id_from_artists'])

                new_tracks_played_data_df['artist_image'] = new_tracks_played_data_df['artist_image'].fillna(new_tracks_played_data_df['image']) 
                
                combined_tracks = pd.concat([new_tracks_played_data_df, pd.DataFrame(tracks_recorded)], ignore_index=True)
                combined_tracks = combined_tracks.drop(columns=["artist_image_from_artists","genres_from_artists"])
                
                daily_register_repository.update_daily_register(
                    user_id = user.id,
                    tracks = json.loads(combined_tracks.to_json(orient="records")),                  
                    date = date.date()
                ) 

                return logging.info(f"Success in retrieving and saving the played tracks on {date.date()} {date.time().replace(microsecond=0)}:00 by the user {user.id}")
            except Exception as e:
                logging.error(f"An error occurred while attempting to store tracks played on {date.date()} {date.time().replace(microsecond=0)}:00 by user {user.id}: {str(e)}") 

    return logging.info(f"The task 'sync_all_users_daily_register' was completed on {date.date()} {date.time().replace(microsecond=0)}:00!")
           