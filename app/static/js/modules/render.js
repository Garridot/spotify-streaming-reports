import { highlightText, capitalizeText } from  './format_text.js' 

const container = document.querySelector(".report--");

export const renderMenuProfile = (data) => {
   
    document.querySelector(".menu-profile").innerHTML =

    `<button><img src="${data["user"]["profile_image_url"]}"> ${data["user"]["username"]}</button>
    <ul class="profile-options">
        <li><a style="font-weight: 600;" href="/logout">Log out <svg style="margin-left: 10px;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M377.9 105.9L500.7 228.7c7.2 7.2 11.3 17.1 11.3 27.3s-4.1 20.1-11.3 27.3L377.9 406.1c-6.4 6.4-15 9.9-24 9.9c-18.7 0-33.9-15.2-33.9-33.9l0-62.1-128 0c-17.7 0-32-14.3-32-32l0-64c0-17.7 14.3-32 32-32l128 0 0-62.1c0-18.7 15.2-33.9 33.9-33.9c9 0 17.6 3.6 24 9.9zM160 96L96 96c-17.7 0-32 14.3-32 32l0 256c0 17.7 14.3 32 32 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-64 0c-53 0-96-43-96-96L0 128C0 75 43 32 96 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32z"/></svg></a></li>
    </ul>`
    
}

export const renderMenuWeeklyReports = (data) => {

    var li = document.createElement("li");
    li.style.margin = "1rem 0.5rem";
    li.innerHTML =
    `<span style="font-size: smaller; font-weight: 600; ">Weekly Reports:</span>`;

    document.querySelector("#menu_history").appendChild(li);               
    
   
    for (const value of data) {

        var li = document.createElement("li");
        li.innerHTML = 
        `
        <button value="${value["weekly_id"]}">${value.time_period["start_date"]} to ${value.time_period["end_date"]}</button>`;
        document.querySelector("#menu_history").appendChild(li);
    }
}

export const renderHeaderStats = (data, time) => {
    var section = document.createElement("section");
    section.className = "wrapped-header"   
    section.innerHTML =      
    `
    <h3>Weekly Summary: <span class="review__highlighted">${time.start_date}</span> to <span class="review__highlighted">${time.end_date}</span></h3>
    <h1>${data.title}</h1>
    <p style="text-align: center;">${data.description}</p> 
    <hr>
    `;
    container.appendChild(section);   

}

export const renderVariationStats = (data) => {
    var total_songs_played = data['tracks_played_this_week']['total_songs_played'];
    var time_listened_this_week = Math.round(parseInt(data['time_listened_this_week']) / 60000, 2); 
    var artists_played_this_week =data['artists_played_this_week'];    
    
    var section = document.createElement("section");
    section.className = "modal_content__review"   
    section.innerHTML =  
    `
    <div class="top-item-modal top-item-modal--review">
        <p>This week, you’ve enjoyed <span class="review__highlighted">${total_songs_played} songs</span>, spending a total of <span class="review__highlighted">${time_listened_this_week} minutes listening</span> to music from <span class="review__highlighted">${artists_played_this_week} different artists.</span> </p>
    </div>             
    `       
    container.appendChild(section);    

    if(data['weekly_variation_tracks'] != undefined){ 

        const weeklyVariationTracks = data['weekly_variation_tracks']['total_track_variations'];         
        const weeklyVariationArtists = data['weekly_variation_artists'];       
        const weeklyVariationTime = data['weekly_variation_time'];

        if (weeklyVariationTracks[0] == "-"){ var resTracks = `has decreased by <span class="review__highlighted">${ weeklyVariationTracks }</span>`;
        }else{ var resTracks = `has increased by <span class="review__highlighted">+${ weeklyVariationTracks }</span>`;
        }
        if (weeklyVariationArtists[0] == "-"){ var resArtists = `has decreased by <span class="review__highlighted">${ weeklyVariationArtists }</span>`;
        }else{ var resArtists = `has increased by <span class="review__highlighted">+${ weeklyVariationArtists }</span>`;
        }
        if (weeklyVariationTime[0] == "-"){ var resTime = `has decreased by <span class="review__highlighted">${ weeklyVariationTime }</span>`;
        }else{ var resTime = `has increased by <span class="review__highlighted">+${ weeklyVariationTime }</span>`;
        }

        var section2 = document.createElement("section");
        section2.className = "modal_content__review"   
        section2.innerHTML =  
        `
        <div class="top-item-modal top-item-modal--review">
            <p>In terms of percentages, the number of songs played this week ${ resTracks }, the total minutes listened to ${ resTime }, and the variety of artists ${ resArtists } compared to last week.</p>
        </div>             
        ` ;

        container.appendChild(section2); 
    }
}

export const renderReportStats = (data) => {
    delete data["title"];
    delete data["description"];     
    
    for (const [key, value] of Object.entries(data)) {

        var section = document.createElement("section");
        section.className = "modal_content__review"   
        section.innerHTML =  
        `
        <div class="top-item-modal top-item-modal--review">
            <p><span class="review__highlighted">${capitalizeText(key)}:</span> ${highlightText(value)}</p>
        </div>             
        `   
        container.appendChild(section); 
    }
}

export const renderTopTrackstStats = (data) => {
    var topDuration = data["most_listened_by_total_duration"];
    var topDurationByDate = data["most_listened_tracks_by_date"];

    var section1 = topTracksRender(topDuration);
    container.appendChild(section1);
    
    var section2 = document.createElement("section");
    section2.className = "modal_content__review"   
    section2.innerHTML =  
    `  
    <div class="modal-content-header">
        <h3>Most listened track by day</h3>
    </div>  
    <div class="model-table">
        <table class="second-table" style="width:100%">                    
        <thead style="text-align:justify;">
            <tr>   
                <th></th>
                <th>Tracks</th>                 
                <th>Day</th>                      
                <th style="text-align:end">Minutes Listened</th>   
            </tr>
        </thead>
        <tbody>
        </tbody>
        </table>
    </div>              
    `;    

    for (const [key, value] of Object.entries(topDurationByDate)) {

        var tr = document.createElement("tr");
        tr.innerHTML = 
        `
        <tr>
            <td><img src="${value["image"]}" alt="${value["album"]}" style="width:50px"> </td>
            <td>${value["song_name"]}</td>
            <td>${ value["day"] }</td> 
            <td style="text-align:end">${(parseInt(value["duration_ms"]) / 60000).toFixed(2)}</td>                 
        </tr>
        `;
        section2.querySelector("tbody").appendChild(tr);
    }

    container.appendChild(section2);    
}

export const renderTopArtiststStats = (data) => {
    var topDuration = data["most_listened_by_total_duration"];
    var topDurationByDate = data["most_listened_artists_by_date"];

    var section1 = topArtistsRender(topDuration);
    

    container.appendChild(section1);
    
    var section2 = document.createElement("section");
    section2.className = "modal_content__review"   
    section2.innerHTML =  
    `  
    <div class="modal-content-header">
        <h3>Most listened artists by day</h3>
    </div>  
    <div class="model-table">
        <table class="second-table" style="width:100%">                    
        <thead style="text-align:justify;">
            <tr>  
                <th>Artists</th>                      
                <th>Day</th>                    
                <th style="text-align:end">Minutes Listened</th>   
            </tr>
        </thead>
        <tbody>
        </tbody>
        </table>
    </div>              
    `;    

    for (const [key, value] of Object.entries(topDurationByDate)) {

        var tr = document.createElement("tr");
        tr.innerHTML = 
        `
        <tr>  
            <td>${value["artist_name"]}</td>
            <td>${value["day"]}</td>  
            <td style="text-align:end">${(parseInt(value["duration_ms"]) / 60000).toFixed(2)}</td>                 
        </tr>
        `;
        section2.querySelector("tbody").appendChild(tr);
    }
    
    container.appendChild(section2);
}

export const renderGenresStats = (data) => {  
    const topGenresListened = data["most_listened_by_total_duration"];    
    var topDurationByDate = data["most_listened_genres_by_date"];

    var section = topGenersRender(topGenresListened);
    
    container.appendChild(section);

    for (const genre in genresData){        
        var div = document.createElement("div");
        div.className = "chart-data";
        div.innerHTML = 
        `        
        <span class="span-label"><div class="chart-label" style="margin: 5px 0;">${genresData[genre].genre} : ${genresData[genre].total_duration} Mins.</div></span>
        <span class="span-bar"><div class="chart-bar" style="width: ${genresData[genre].rate}%;"></div></span>        
        `;
        section.querySelector(".top-item-modal--genres").appendChild(div);
    };

    var section2 = document.createElement("section");
    section2.className = "modal_content__review"   
    section2.innerHTML =  
    `  
    <div class="modal-content-header">
        <h3>Most listened genres by day</h3>
    </div>  
    <div class="model-table">
        <table class="second-table" style="width:100%">                    
        <thead style="text-align:justify;">
            <tr>                             
                <th>Day</th>  
                <th>Genres</th>    
                <th style="text-align:end">Minutes Listened</th>   
            </tr>
        </thead>
        <tbody>
        </tbody>
        </table>
    </div>              
    `;  
    
    for (const [key, value] of Object.entries(topDurationByDate)) {

        var tr = document.createElement("tr");
        tr.innerHTML = 
        `
        <tr>  
            <td>${value["day"]}</td>                       
            <td>${value["genres"]}</td>  
            <td style="text-align:end">${(parseInt(value["duration_ms"]) / 60000).toFixed(2)}</td>                 
        </tr>
        `;
        section2.querySelector("tbody").appendChild(tr);
    }

    container.appendChild(section2);
         
}


export const renderExtraStats  = (data) => {

    const topDuration = data["most_album_listened"][0];
    
    var section = topAlbumRender(topDuration);
    container.appendChild(section);

    var section2 = document.createElement("section");
    section2.className = "modal_content__review";
    section2.innerHTML =  
    `
    <div>                                                
        <ul>                                                
            <li style="list-style:none;">
                <p style="font-weight: 600;">Your busiest day this week:</p>
                <h1 style="font-size: larger; color: var(--color-highlight);">${data["top_day"][0]["day"]}</h1>                
                <p style="font-weight: 600;">Tracks Listened: <span class="review__highlighted">${data["top_day"][0]["songs_played"]}</span></p>              
            </li>               
        </ul>         
    </div>  
    <div>                                                
        <ul>                                                
            <li style="list-style:none;">
                <p style="font-weight: 600;">Your busiest hour this week:</p>
                <h1 style="font-size: larger; color: var(--color-highlight);">${data["top_hours"][0]["hours"]}</h1>                
                <p style="font-weight: 600;">Tracks Listened: <span class="review__highlighted">${data["top_hours"][0]["songs_played"]}</span></p>              
            </li>               
        </ul>         
    </div>`; 

    container.appendChild(section2);
}

export const renderLastActivity = (data) => {

    var topTracks = data["most_tracks_listened"];
    var section1 = topTracksRender(topTracks);
    container.appendChild(section1);

    var topArtists = data["most_artists_listened"];
    var section2 = topArtistsRender(topArtists);
    container.appendChild(section2);

    
    const topGenres = data["most_genres_listened"]; 
    var section3 = topGenersRender(topGenres);
    container.appendChild(section3);

    
    const topAlbum = data["most_album_listened"][0];      
    var section4 = topAlbumRender(topAlbum);    
    container.appendChild(section4);
}

const topTracksRender = (data) => {
    var section = document.createElement("section");
    section.className = "modal_content__review"   
    section.innerHTML =  
    `
    <div class="top-item-modal--tracks">                                               
        <ul>                                                
            <li style="list-style:none;">
                <h3>Your Most Listened Track:</h3>
                <h1>${data[0]["song_name"]} - ${data[0]["artist_name"]}</h1>                
                <h3>Minutes Listened: <span class="review__highlighted">${(parseInt(data[0]["duration_ms"]) / 60000).toFixed(2)}</span></h3>              
            </li>               
        </ul> 
        <div class="top-item-modal-image">
            <img src="${data[0]["image"]}" alt="${data[0]["album"]}"> 
        </div>
    </div> 
    <hr> 
    <div class="model-table">
        <table class="main-table" style="width:100%">                    
        <thead style="text-align:justify;">
            <tr>                             
                <th></th>  
                <th>Tracks</th>                  
                <th>Artists</th>                  
                <th style="text-align:end">Minutes Listened</th>   
            </tr>
        </thead>
        <tbody>
        </tbody>
        </table>
    </div>            
    `; 

    for (const [key, value] of Object.entries(data).slice(1)) {

        var tr = document.createElement("tr");
        tr.innerHTML = 
        `
        <tr>  
            <td><img src="${value["image"]}" alt="${value["album"]}" style="width:50px"></td>                       
            <td>${value["song_name"]}</td>         
            <td>${value["artist_name"]}</td>                                
            <td style="text-align:end">${(parseInt(value["duration_ms"]) / 60000).toFixed(2)}</td>                
        </tr>
        `;
        section.querySelector("tbody").appendChild(tr);
    }

    return section;
}
const topArtistsRender = (data) => {
    var section = document.createElement("section");
    section.className = "modal_content__review"   
    section.innerHTML =  
    `
    
    <div class="top-item-modal--tracks">                                                
        <ul>                                                
            <li style="list-style:none;">
                <h3>Your Most Listened Artist:</h3>
                <h1>${data[0]["artist_name"]}</h1>                
                <h3>Minutes Listened: <span class="review__highlighted">${(parseInt(data[0]["duration_ms"]) / 60000).toFixed(2)}</span></h3>              
            </li>               
        </ul> 
        <div class="top-item-modal-image">
            <div class="top-item-modal-image-wrapper" style="background:url(${data[0]["artist_image"]}) center center/cover;"></div>
        </div>
    </div> 
    <hr> 
    <div class="model-table">
        <table class="main-table" style="width:100%">                    
        <thead style="text-align:justify;">
            <tr>                             
                <th>#</th>                   
                <th>Artists</th>                  
                <th style="text-align:end">Minutes Listened</th>   
            </tr>
        </thead>
        <tbody>
        </tbody>
        </table>
    </div>            
    `; 

    for (const [key, value] of Object.entries(data).slice(1)) {

        var tr = document.createElement("tr");
        tr.innerHTML = 
        `
        <tr>  
            <td>${parseInt(key) + 1}</td>   
            <td>${value["artist_name"]}</td>                                
            <td style="text-align:end">${(parseInt(value["duration_ms"]) / 60000).toFixed(2)}</td>                
        </tr>
        `;
        section.querySelector("tbody").appendChild(tr);
    }

    return section;
}
const topGenersRender = (data) =>  {
    const genresData = [        
        { 
            "genre": capitalizeText(data[0]["genres"]), 
            "total_duration": (parseInt(data[0]["duration_ms"]) / 60000).toFixed(2), 
            "rate": 100
        },
        {
            "genre": capitalizeText(data[1]["genres"]),
            "total_duration": (parseInt(data[1]["duration_ms"]) / 60000).toFixed(2),
            "rate": ( (data[1]["duration_ms"] / data[0]["duration_ms"]) * 100).toFixed(2)
        },
        {
            "genre": capitalizeText(data[2]["genres"]),
            "total_duration": (parseInt(data[2]["duration_ms"]) / 60000).toFixed(2),
            "rate": ( (data[2]["duration_ms"] / data[0]["duration_ms"]) * 100).toFixed(2)
        },
        {
            "genre": capitalizeText(data[3]["genres"]),
            "total_duration": (parseInt(data[3]["duration_ms"]) / 60000).toFixed(2),
            "rate": ( (data[3]["duration_ms"] / data[0]["duration_ms"]) * 100).toFixed(2)
        },
        {
            "genre": capitalizeText(data[4]["genres"]),
            "total_duration": (parseInt(data[4]["duration_ms"]) / 60000).toFixed(2),
            "rate": ( (data[4]["duration_ms"] / data[0]["duration_ms"]) * 100).toFixed(2)
        }
    ];

    var section = document.createElement("section");
    section.className = "modal_content__review";
    section.innerHTML =  
    `
    <div class="modal-content-header">
        <h3>Top Genres Right Now:</h3>
        <hr style="width: 100%;">
    </div>
    <div class="top-item-modal--genres" style="margin: 2rem 0 0;"></div>              
    `;   

    for (const genre in genresData){        
        var div = document.createElement("div");
        div.className = "chart-data";
        div.innerHTML = 
        `        
        <span class="span-label"><div class="chart-label" style="margin: 5px 0;">${genresData[genre].genre} : ${genresData[genre].total_duration} Mins.</div></span>
        <span class="span-bar"><div class="chart-bar" style="width: ${genresData[genre].rate}%;"></div></span>        
        `;
        section.querySelector(".top-item-modal--genres").appendChild(div);
    };

    return section;
}
const topAlbumRender = (data) => {
    var section = document.createElement("section");
    section.className = "modal_content__review"   
    section.innerHTML =  
    `
    <div class="top-item-modal--tracks">                                                
        <ul>                                                
            <li style="list-style:none;">
                <h3>Your Most Listened Album:</h3>
                <h1>${data["album"]} - ${data["artist_name"]}</h1>                
                <h3>Minutes Listened: <span class="review__highlighted">${(parseInt(data["duration_ms"]) / 60000).toFixed(2)}</span></h3>              
            </li>               
        </ul> 
        <div class="top-item-modal-image">
            <img src="${data["image"]}" alt="${data["album"]}"> 
        </div>
    </div>                 
    `; 

    return section;
}