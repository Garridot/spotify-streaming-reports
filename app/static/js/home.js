import { getUserInfo, getUserWeeklyReports, getUserStats } from './modules/fetchs.js'; 
import { 
    renderMenuProfile, renderMenuWeeklyReports, renderHeaderStats, 
    renderReportStats,renderTopTrackstStats, renderTopArtiststStats, 
    renderVariationStats,renderGenresStats, renderExtraStats } from './modules/render.js'; 

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
        document.querySelector(".report--").innerHTML =
        `
        <div class="intro-text">
            <p>Hello ${userInfo["user"]["username"]}, you can see your weekly reports in more detail here, as you receive them via email. </p>
        </div>
        `;
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
                var weekly_id = i.value;
                document.querySelector(".report--").innerHTML = "";
                const newUserStats = await getUserStats(weekly_id); 

                var stats = newUserStats["user_stats"];

                await renderStats(stats);
            })
        })
    }; 

    document.querySelector(".menu-profile button").addEventListener("click", () => {
        document.querySelector(".profile-options").classList.toggle("view");
    })

}

init(); 