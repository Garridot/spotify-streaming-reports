import { getUserInfo } from './modules/fetchs.js'; 



async function init() {
    const userInfo = await getUserInfo();
    console.log(userInfo)
    document.querySelector("body").innerHTML =
    `
    <div class="intro-text">
        <p>Hello ${userInfo["user"]["username"]}, you can see your weekly reports in more detail here, as you receive them via email. </p>
    </div>
    `;
}


init(); 
