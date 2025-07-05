
document.addEventListener('DOMContentLoaded', function() {
    const fontPreloads = document.querySelectorAll('.font-preload');
    
    fontPreloads.forEach(function(preload) {
        preload.onload = function() {
            this.onload = null;
            this.rel = 'stylesheet';
        };
    });
}); 