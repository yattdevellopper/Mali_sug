// static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des tooltips Bootstrap (si vous en utilisez)
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })

    // Fermer les messages flash après un certain temps (si non fait par Bootstrap)
    setTimeout(function() {
        var alerts = document.querySelectorAll('.messages-container .alert');
        alerts.forEach(function(alert) {
            new bootstrap.Alert(alert).close();
        });
    }, 5000); // 5 secondes
});