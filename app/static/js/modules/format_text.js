export function highlightText(text) {
    // Reemplazar **texto** por <span>
    let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<span class="review__highlighted">$1</span>');
  
    // Reemplazar *texto* por <em>
    formattedText = formattedText.replace(/\*(.*?)\*/g, '<em class="review__highlighted">$1</em>');
  
    return formattedText;
}

export function capitalizeText(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}