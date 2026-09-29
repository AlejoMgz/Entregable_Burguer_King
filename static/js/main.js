document.addEventListener('DOMContentLoaded', () => {

    // 1. Cerrar automáticamente los mensajes a los 5 segundos
    document.querySelectorAll('.auto-cerrar').forEach(alerta => {
        setTimeout(() => bootstrap.Alert.getOrCreateInstance(alerta).close(), 5000);
    });

    // 2. Validación en el navegador (Bootstrap) + contraseñas iguales
    document.querySelectorAll('form[data-validar]').forEach(form => {
        form.addEventListener('submit', e => {
            const p1 = form.querySelector('#id_password1');
            const p2 = form.querySelector('#id_password2');
            if (p1 && p2) {
                p2.setCustomValidity(p1.value !== p2.value ? 'Las contraseñas no coinciden' : '');
            }
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // 3. Buscador en vivo de productos
    const buscador = document.getElementById('buscador');
    if (buscador) {
        buscador.addEventListener('input', () => {
            const texto = buscador.value.toLowerCase();
            document.querySelectorAll('.item-producto').forEach(item => {
                const visible = item.dataset.nombre.includes(texto);
                item.style.display = visible ? '' : 'none';
            });
        });
    }

    // 4. Confirmar antes de vaciar/quitar (formularios con data-confirmar)
    document.querySelectorAll('form[data-confirmar]').forEach(form => {
        form.addEventListener('submit', e => {
            if (!confirm(form.dataset.confirmar)) e.preventDefault();
        });
    });

    // 5. Botón "volver arriba"
    const btn = document.getElementById('btn-subir');
    if (btn) {
        window.addEventListener('scroll', () => {
            btn.style.display = window.scrollY > 300 ? 'block' : 'none';
        });
        btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    }
});