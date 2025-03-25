
window.onload = function() {
    const salesData = JSON.parse(document.getElementById('sales-data').textContent);
    const ctx = document.getElementById('salesChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: salesData.map(item => item.product__name),
            datasets: [{
                label: 'Total Sales',
                data: salesData.map(item => item.total_sold),
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        }
    });
}
