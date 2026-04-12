// Inclui topbar e sidebar em todas as páginas
function includeHTML() {
    fetch('topbar.html').then(r => r.text()).then(html => {
        document.body.insertAdjacentHTML('afterbegin', html);
    });
    fetch('sidebar.html').then(r => r.text()).then(html => {
        document.body.insertAdjacentHTML('afterbegin', html);
    });
}
window.addEventListener('DOMContentLoaded', includeHTML);