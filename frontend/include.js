// Redireciona para login se não estiver autenticado
if (!localStorage.getItem('auth')) {
    window.location.href = 'login.html';
}

// Inclui topbar e sidebar em todas as páginas
function includeHTML() {
    fetch('topbar.html').then(r => r.text()).then(html => {
        document.body.insertAdjacentHTML('afterbegin', html);
        setTimeout(() => {
            const btn = document.getElementById('logout-btn');
            if (btn) {
                btn.onclick = function(event) {
                    event.preventDefault();
                    localStorage.removeItem('username');
                    localStorage.removeItem('auth');
                    window.location.href = 'login.html';
                };
            }
        }, 100);
    });
    fetch('sidebar.html').then(r => r.text()).then(html => {
        document.body.insertAdjacentHTML('afterbegin', html);
    });
}
window.addEventListener('DOMContentLoaded', includeHTML);