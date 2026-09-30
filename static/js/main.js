/* ==========================================================================
   HUMAN-CENTERED AI IN SMART FARMING - JAVASCRIPT
   Interactions, Sidebar Toggle, Explanation Tabs & Demo Helpers
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile Sidebar Navigation Toggle
    const mobileToggleBtn = document.getElementById('mobileToggleBtn');
    const sidebar = document.getElementById('sidebar');
    
    if (mobileToggleBtn && sidebar) {
        mobileToggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('open');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function (event) {
            if (window.innerWidth <= 992) {
                if (!sidebar.contains(event.target) && !mobileToggleBtn.contains(event.target)) {
                    sidebar.classList.remove('open');
                }
            }
        });
    }

    // 2. Tab Switcher for Human-Centered AI Explanations (Simple vs Technical)
    const tabItems = document.querySelectorAll('.tab-item');
    tabItems.forEach(tab => {
        tab.addEventListener('click', function () {
            const target = this.getAttribute('data-tab-target');
            
            // Remove active class from sibling tabs
            const parentTabs = this.closest('.tab-group');
            if (parentTabs) {
                parentTabs.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
            }
            this.classList.add('active');

            // Hide/Show tab contents
            const contentGroup = document.getElementById('tabContentContainer');
            if (contentGroup) {
                contentGroup.querySelectorAll('.tab-content-panel').forEach(panel => {
                    if (panel.id === target) {
                        panel.style.display = 'block';
                    } else {
                        panel.style.display = 'none';
                    }
                });
            }
        });
    });

    // 3. Auto-Dismiss Flash Alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

// Helper function to fill sample form data for quick testing in demo mode
function fillSampleData(formType) {
    if (formType === 'crop') {
        const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
        setVal('nitrogen', 90);
        setVal('phosphorus', 42);
        setVal('potassium', 43);
        setVal('temperature', 20.8);
        setVal('humidity', 82.0);
        setVal('ph', 6.5);
        setVal('rainfall', 202.9);
    } else if (formType === 'soil') {
        const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
        setVal('nitrogen', 85);
        setVal('phosphorus', 38);
        setVal('potassium', 40);
        setVal('ph', 6.8);
        setVal('moisture', 45);
    }
}
