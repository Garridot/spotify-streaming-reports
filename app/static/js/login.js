import { getSpotyAuth } from './modules/fetchs.js'; 

const loginBTN = document.querySelector(".form_link_buttom button");

async function init() {
    const authLink = await getSpotyAuth();
    window.location.href = authLink["spotify_auth_url"];
}

loginBTN.addEventListener("click", ()=> {    
    init(); 
})