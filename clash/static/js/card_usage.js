document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/card_usage')
        .then(response => response.json())
        .then(data => {
            // Process and display card usage data
            console.log(data);
            // TODO: Add chart or table to visualize data
        });
});