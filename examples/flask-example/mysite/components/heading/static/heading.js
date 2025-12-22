/**
 * Heading component JavaScript
 *
 * This file demonstrates colocated JavaScript assets with components.
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Heading component loaded successfully!');

        // Add hover effect to heading
        const headingTitle = document.querySelector('.heading-title');
        if (headingTitle) {
            headingTitle.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.05)';
                this.style.transition = 'transform 0.3s ease';
            });

            headingTitle.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
            });
        }

        // Add click interaction
        const container = document.querySelector('.heading-container');
        if (container) {
            let clickCount = 0;
            container.addEventListener('click', function() {
                clickCount++;
                console.log('Container clicked:', clickCount, 'times');
            });
        }

        // Log tdom-path info
        console.log('tdom-path: Component assets loaded via automatic path resolution');
    });
})();
