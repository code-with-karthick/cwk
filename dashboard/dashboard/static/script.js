document.addEventListener("DOMContentLoaded", () => {
    // 1. Live Clock & Date
    function updateDateTime() {
        const now = new Date();
        const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' };
        document.getElementById('datetime').textContent = now.toLocaleDateString('en-US', options);
    }
    setInterval(updateDateTime, 1000);
    updateDateTime();

    // 2. Dark Mode Toggle
    const themeToggle = document.getElementById('themeToggle');
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        themeToggle.innerHTML = isDark ? '<i class="fa-solid fa-sun"></i> Light Mode' : '<i class="fa-solid fa-moon"></i> Dark Mode';
    });

    // 3. Fetch Dashboard Data & Counting with Date Filter Support
    let courseChartInstance = null;

    function fetchDashboardData(startDate = '', endDate = '') {
        let url = '/api/dashboard-data';
        if (startDate && endDate) {
            url += `?start_date=${startDate}&end_date=${endDate}`;
        }

        fetch(url)
            .then(res => res.json())
            .then(data => {
                // Update Overview Cards Counting
                document.getElementById('total_students').textContent = data.total_students;
                document.getElementById('active_students').textContent = data.active_students;
                document.getElementById('today_walkins').textContent = data.today_walkins;
                document.getElementById('today_admissions').textContent = data.today_admissions;
                document.getElementById('this_month_join').textContent = data.this_month_join;
                document.getElementById('prev_month_join').textContent = data.prev_month_join;
                document.getElementById('this_year_join').textContent = data.this_year_join;
                document.getElementById('certificate_issued').textContent = data.certificate_issued;
                document.getElementById('pending_revenue').textContent = '₹' + data.pending_revenue.toLocaleString();
                document.getElementById('study_material_distributed').textContent = data.study_material_distributed;
                document.getElementById('amount_paid').textContent = '₹' + data.amount_paid.toLocaleString();
                document.getElementById('balance_due').textContent = '₹' + data.balance_due.toLocaleString();

                // Update Other Tabs
                document.getElementById('st_active').textContent = data.active_students;
                document.getElementById('st_walk').textContent = data.today_walkins;
                document.getElementById('st_adm').textContent = data.today_admissions;

                document.getElementById('fn_paid').textContent = '₹' + data.amount_paid.toLocaleString();
                document.getElementById('fn_due').textContent = '₹' + data.balance_due.toLocaleString();
                document.getElementById('fn_rev').textContent = '₹' + data.pending_revenue.toLocaleString();

                document.getElementById('rp_cert').textContent = data.certificate_issued;
                document.getElementById('rp_mat').textContent = data.study_material_distributed;

                // Render Chart
                renderChart(data.chart_labels, data.chart_data);
            })
            .catch(err => console.error('Error fetching dashboard data:', err));
    }

    function renderChart(labels, values) {
        const ctx = document.getElementById('courseChart').getContext('2d');
        if (courseChartInstance) {
            courseChartInstance.destroy();
        }
        courseChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Enrollments',
                    data: values,
                    backgroundColor: '#00d2ff',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } },
                    y: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: '#212c3d' } }
                }
            }
        });
    }

    // Initial load
    fetchDashboardData();

    // Filter Buttons Click Events
    document.getElementById('filterBtn').addEventListener('click', () => {
        const start = document.getElementById('startDate').value;
        const end = document.getElementById('endDate').value;
        if (!start || !end) {
            alert('Please select both Start and End dates!');
            return;
        }
        fetchDashboardData(start, end);
    });

    document.getElementById('resetBtn').addEventListener('click', () => {
        document.getElementById('startDate').value = '';
        document.getElementById('endDate').value = '';
        fetchDashboardData();
    });
});

// Tab Switching
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active-tab'));
    document.querySelectorAll('.sidebar-menu li').forEach(el => el.classList.remove('active'));

    document.getElementById('tab-' + tabName).classList.add('active-tab');
    event.currentTarget.classList.add('active');
}