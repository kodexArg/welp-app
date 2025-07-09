/**
 * Interactividad perfecta para tickets
 * JavaScript mínimo y eficiente
 */

// Delegación de eventos global - una sola vez
document.addEventListener('click', event => {
    const ticket = event.target.closest('.ticket-container');
    if (!ticket || event.target.closest('button, a, input, select, textarea')) return;
    
    const details = ticket.querySelector('details');
    if (details && !event.target.closest('summary')) {
        event.preventDefault();
        ticket.querySelector('summary').click();
            }
});
        
// Soporte teclado minimalista
document.addEventListener('keydown', event => {
    if ((event.key === 'Enter' || event.key === ' ') && 
        event.target.closest('.ticket-container') && 
        !event.target.closest('button, a, input, select, textarea')) {
        event.preventDefault();
        event.target.closest('.ticket-container').querySelector('summary').click();
    }
}); 