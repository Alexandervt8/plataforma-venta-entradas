document.addEventListener('DOMContentLoaded', () => {
    // --- 1. Desvanecimiento automático de mensajes flash ---
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach((msg) => {
        // Opción de cerrar manualmente
        const closeBtn = msg.querySelector('.flash-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                msg.style.opacity = '0';
                msg.style.transform = 'translateY(-10px)';
                setTimeout(() => msg.remove(), 300);
            });
        }
        
        // Auto-cerrar después de 4 segundos
        setTimeout(() => {
            if (msg.parentNode) {
                msg.style.transition = 'all 0.5s ease';
                msg.style.opacity = '0';
                msg.style.transform = 'translateY(-10px)';
                setTimeout(() => msg.remove(), 500);
            }
        }, 4000);
    });

    // --- 2. Cálculos dinámicos en la página de Compra de Entradas ---
    const quantityInput = document.getElementById('purchase-quantity');
    const pricePerTicketElement = document.getElementById('price-per-ticket');
    const totalPriceElement = document.getElementById('total-price');
    const quantitySummaryElement = document.getElementById('quantity-summary');
    const purchaseBtn = document.getElementById('purchase-btn');
    const stockElement = document.getElementById('event-stock');

    if (quantityInput && pricePerTicketElement && totalPriceElement) {
        const price = parseFloat(pricePerTicketElement.dataset.price);
        const maxStock = parseInt(stockElement ? stockElement.dataset.stock : 999999);

        const calculateTotal = () => {
            const qty = parseInt(quantityInput.value) || 0;
            const errorElement = document.getElementById('quantity-error');

            // Validaciones locales en caliente
            if (qty <= 0) {
                if (errorElement) {
                    errorElement.textContent = 'La cantidad debe ser mayor a 0.';
                    errorElement.style.display = 'block';
                }
                purchaseBtn.disabled = true;
                totalPriceElement.textContent = 'S/ 0.00';
                if (quantitySummaryElement) quantitySummaryElement.textContent = '0';
            } else if (qty > maxStock) {
                if (errorElement) {
                    errorElement.textContent = `No puedes comprar más del stock disponible (${maxStock} entradas).`;
                    errorElement.style.display = 'block';
                }
                purchaseBtn.disabled = true;
                totalPriceElement.textContent = 'S/ 0.00';
                if (quantitySummaryElement) quantitySummaryElement.textContent = qty.toString();
            } else {
                if (errorElement) {
                    errorElement.style.display = 'none';
                }
                purchaseBtn.disabled = false;
                const total = price * qty;
                totalPriceElement.textContent = `S/ ${total.toFixed(2)}`;
                if (quantitySummaryElement) quantitySummaryElement.textContent = qty.toString();
            }
        };

        quantityInput.addEventListener('input', calculateTotal);
        quantityInput.addEventListener('change', calculateTotal);
        // Inicializar el cálculo al cargar
        calculateTotal();
    }

    // --- 3. Validación de Formularios en el Cliente (Registro / Login) ---
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            let valid = true;
            
            const name = document.getElementById('name');
            const email = document.getElementById('email');
            const password = document.getElementById('password');

            // Resetear textos de error
            document.querySelectorAll('.form-error-text').forEach(el => el.style.display = 'none');

            // Nombre vacío
            if (name && name.value.trim() === '') {
                showError('name-error', 'El nombre es obligatorio.');
                valid = false;
            }

            // Email vacío o inválido
            if (email) {
                const emailVal = email.value.trim();
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (emailVal === '') {
                    showError('email-error', 'El correo electrónico es obligatorio.');
                    valid = false;
                } else if (!emailRegex.test(emailVal)) {
                    showError('email-error', 'Por favor ingresa un correo electrónico válido.');
                    valid = false;
                }
            }

            // Contraseña vacía o menor a 6
            if (password) {
                const passVal = password.value;
                if (passVal === '') {
                    showError('password-error', 'La contraseña es obligatoria.');
                    valid = false;
                } else if (passVal.length < 6) {
                    showError('password-error', 'La contraseña debe tener al menos 6 caracteres.');
                    valid = false;
                }
            }

            if (!valid) {
                e.preventDefault();
            }
        });
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            let valid = true;
            
            const email = document.getElementById('email');
            const password = document.getElementById('password');

            // Resetear errores
            document.querySelectorAll('.form-error-text').forEach(el => el.style.display = 'none');

            if (email && email.value.trim() === '') {
                showError('email-error', 'El correo electrónico es obligatorio.');
                valid = false;
            }

            if (password && password.value === '') {
                showError('password-error', 'La contraseña es obligatoria.');
                valid = false;
            }

            if (!valid) {
                e.preventDefault();
            }
        });
    }

    // Función auxiliar para mostrar errores de formulario
    function showError(id, message) {
        const errEl = document.getElementById(id);
        if (errEl) {
            errEl.textContent = message;
            errEl.style.display = 'block';
        }
    }
});
