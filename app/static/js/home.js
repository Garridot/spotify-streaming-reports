import { getUserInfo, getUserWeeklyReports, getUserStats, getUserActivity } from './modules/fetchs.js'; 
import { 
    renderMenuProfile, renderMenuWeeklyReports, renderHeaderStats, 
    renderReportStats,renderTopTrackstStats, renderTopArtiststStats, 
    renderVariationStats,renderGenresStats, renderExtraStats, renderLastActivity } from './modules/render.js'; 

async function renderStats (data) {       
    renderHeaderStats(data["report"],data["time_period"]);       
    renderTopTrackstStats(data["top_tracks"]);
    renderTopArtiststStats(data["top_artists"]);
    renderVariationStats(data["extra_data"]);    
    renderGenresStats(data["top_genres"]);
    renderExtraStats(data["extra_data"]);
    renderReportStats(data["report"]);
}

async function init() {    
    const userInfo = await getUserInfo();  

    renderMenuProfile(userInfo);
    
    const userWeeklyReports = await getUserWeeklyReports();    

    if (userWeeklyReports["user_history_stats"] == null) {  
        
        var li = document.createElement("li");
        li.style.margin = "1rem 0.5rem";
        li.innerHTML =
        `<span style="font-size: smaller; font-weight: 600; ">Weekly Reports:</span>`;

        document.querySelector("#menu_history").appendChild(li); 

        document.querySelector(".report--").innerHTML =
        `<section class="modal_content__review">
            <p style="text-align: center;">Hello <span class="review__highlighted">${userInfo["user"]["username"]}</span>, you can view your detailed weekly reports, including your most listened tracks, artists, and genres, as well as highlighted patterns and recommendations. You will be notified via email every week.</p>
        </section>`;

        const lastActivity = await getUserActivity(); 
              
        renderLastActivity(lastActivity["user_last_activity"]);

    } 
    else{
        renderMenuWeeklyReports(userWeeklyReports["user_history_stats"]); 

        document.querySelector(".menu-btn svg").addEventListener("click", () => {
            document.querySelector(".menu--").classList.toggle("view");
            document.querySelector(".menu_history").classList.toggle("view");
            document.querySelector(".menu-profile").classList.toggle("view");
        } )
        
        const lastReport = userWeeklyReports["user_history_stats"][0];

        const userStats = await getUserStats(lastReport["weekly_id"]);  
        
        var stats = userStats["user_stats"];

        await renderStats(stats);


        document.querySelectorAll(".menu_history button").forEach(i => {
            i.addEventListener("click",async () => {
                document.querySelector(".menu--").classList.toggle("view");
                document.querySelector(".menu_history").classList.toggle("view");
                document.querySelector(".menu-profile").classList.toggle("view");
                var weekly_id = i.value;
                document.querySelector(".report--").innerHTML = "";
                const newUserStats = await getUserStats(weekly_id); 

                var stats = newUserStats["user_stats"];

                await renderStats(stats);
            })
        })
    }; 

}

init(); 

document.querySelector(".menu-btn svg").addEventListener("click", () => { 
    document.querySelector(".menu--").classList.toggle("view");
    document.querySelector(".menu_history").classList.toggle("view");
    document.querySelector(".menu-profile").classList.toggle("view");
})