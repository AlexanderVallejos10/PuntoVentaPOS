(() => {
    const config = document.getElementById('posConfig');
    if (!config) return;

    const $ = (id) => document.getElementById(id);
    const toNumber = (value) => Number(String(value || '0').replace(',', '.')) || 0;
    const totalBase = toNumber(config.dataset.total);

    const scanner = $('codigoScanner');
    const formPago = $('formPago');
    const formCliente = $('formCrearCliente');
    const tipoDocumento = $('tipoDocumentoCliente');
    const numeroDocumento = $('numeroDocumentoCliente');
    const btnBuscarCliente = $('btnBuscarCliente');

    function enfocarScanner(event) {
        if (!scanner) return;
        const target = event.target;
        if (target.closest('.modal') || target.closest('.offcanvas') || ['INPUT', 'SELECT', 'TEXTAREA', 'BUTTON', 'A'].includes(target.tagName)) return;
        scanner.focus();
    }

    function actualizarDocumentoCliente() {
        if (!tipoDocumento || !numeroDocumento || !btnBuscarCliente) return;
        const tipo = tipoDocumento.value;
        const usaDocumento = tipo !== 'SD';
        numeroDocumento.disabled = !usaDocumento;
        btnBuscarCliente.disabled = !(tipo === 'DNI' || tipo === 'RUC');

        if (!usaDocumento) {
            numeroDocumento.value = '';
            numeroDocumento.placeholder = 'No necesario';
        } else {
            numeroDocumento.placeholder = 'Número de documento';
        }
    }

    function actualizarPago() {
        const cortesia = $('cortesiaCheck')?.checked || false;
        const envioActivo = $('envioCheck')?.checked || false;
        const costoEnvio = envioActivo ? toNumber($('costoEnvio')?.value) : 0;
        const descuentoPorcentaje = Math.min(Math.max(toNumber($('descuentoPorcentaje')?.value), 0), 100);
        const metodoPago = $('metodoPago')?.value || 'EFECTIVO';
        const montoRecibido = $('montoRecibido');

        let descuento = totalBase * descuentoPorcentaje / 100;
        let base = totalBase - descuento;
        let impuesto = base * 0.18;
        let totalFinal = base + impuesto + costoEnvio;

        if (cortesia) {
            descuento = totalBase;
            impuesto = 0;
            totalFinal = 0;
        }

        if ($('envioBox')) $('envioBox').classList.toggle('d-none', !envioActivo);
        if ($('alertaCortesia')) $('alertaCortesia').classList.toggle('d-none', !cortesia);

        if (montoRecibido) {
            montoRecibido.disabled = cortesia;
            if (cortesia) montoRecibido.value = '0.00';
            if (!cortesia && metodoPago !== 'EFECTIVO') montoRecibido.value = totalFinal.toFixed(2);
        }

        if ($('labelMontoRecibido')) $('labelMontoRecibido').innerText = `${metodoPago.toLowerCase()} recibido`;
        if ($('descuentoVenta')) $('descuentoVenta').value = descuento.toFixed(2);
        if ($('impuestoVenta')) $('impuestoVenta').value = impuesto.toFixed(2);
        if ($('totalFinalVenta')) $('totalFinalVenta').value = totalFinal.toFixed(2);
        if ($('totalPagarTexto')) $('totalPagarTexto').innerText = `S/ ${totalFinal.toFixed(2)}`;
        if ($('descuentoPanel')) $('descuentoPanel').innerText = `-S/ ${descuento.toFixed(2)}`;
        if ($('impuestoPanel')) $('impuestoPanel').innerText = `S/ ${impuesto.toFixed(2)}`;
        if ($('envioPanel')) $('envioPanel').innerText = `S/ ${costoEnvio.toFixed(2)}`;
        if ($('totalPanel')) $('totalPanel').innerText = `S/ ${totalFinal.toFixed(2)}`;
    }

    function validarPago(event) {
        const cortesia = $('cortesiaCheck')?.checked || false;
        const monto = $('montoRecibido');
        const errorMonto = $('errorMonto');
        const cliente = $('clienteId');
        const opcion = cliente?.options[cliente.selectedIndex];
        const tipoCliente = opcion?.dataset.tipo || 'SD';
        const numeroCliente = opcion?.dataset.documento || '';
        const totalFinal = toNumber($('totalFinalVenta')?.value);
        const tipoComprobante = $('tipoComprobante')?.value || 'BOLETA';

        if (!cortesia && (!monto?.value || toNumber(monto.value) <= 0)) {
            event.preventDefault();
            errorMonto?.classList.remove('d-none');
            monto?.focus();
            return;
        }

        if (tipoComprobante === 'FACTURA' && (!cliente?.value || tipoCliente !== 'RUC' || !numeroCliente)) {
            event.preventDefault();
            alert('Para factura selecciona un cliente con RUC válido.');
            return;
        }

        if (totalFinal > 700 && (!cliente?.value || tipoCliente === 'SD' || !numeroCliente)) {
            event.preventDefault();
            alert('Para ventas mayores a S/ 700 registra el documento del cliente.');
            return;
        }

        errorMonto?.classList.add('d-none');
    }

    function consultarDocumento() {
        const tipo = tipoDocumento?.value;
        const numero = numeroDocumento?.value.trim();
        if (!(tipo === 'DNI' || tipo === 'RUC')) return alert('La consulta automática solo aplica para DNI o RUC.');
        if (!numero) return alert('Ingrese el número de documento.');

        const url = `${config.dataset.documentoUrl}?tipo_documento=${encodeURIComponent(tipo)}&numero_documento=${encodeURIComponent(numero)}`;
        btnBuscarCliente.disabled = true;
        btnBuscarCliente.innerText = 'Consultando...';

        fetch(url)
            .then((response) => response.json())
            .then((data) => {
                if (data.ok) {
                    $('nombreCliente').value = data.nombre;
                } else {
                    alert(data.mensaje || 'No se encontró información.');
                }
            })
            .catch(() => alert('No se pudo consultar el documento.'))
            .finally(() => {
                btnBuscarCliente.disabled = false;
                btnBuscarCliente.innerText = 'Consultar';
            });
    }

    function guardarCliente(event) {
        event.preventDefault();

        fetch(config.dataset.clienteUrl, {
            method: 'POST',
            body: new FormData(formCliente),
            headers: { 'X-CSRFToken': config.dataset.csrf },
        })
            .then((response) => response.json())
            .then((data) => {
                if (!data.ok) return alert(data.error || 'No se pudo crear el cliente.');

                const select = $('clienteId');
                const texto = data.numero_documento ? `${data.nombre} - ${data.numero_documento}` : data.nombre;
                const option = new Option(texto, data.id, true, true);
                option.dataset.tipo = data.tipo_documento || 'SD';
                option.dataset.documento = data.numero_documento || '';
                select.add(option);
                select.value = data.id;

                bootstrap.Modal.getOrCreateInstance($('modalCrearCliente')).hide();
                formCliente.reset();
                actualizarDocumentoCliente();
            })
            .catch(() => alert('No se pudo guardar el cliente.'));
    }

    scanner?.focus();
    document.addEventListener('click', enfocarScanner);
    ['descuentoPorcentaje', 'metodoPago', 'cortesiaCheck', 'envioCheck', 'costoEnvio', 'tipoComprobante'].forEach((id) => {
        $(id)?.addEventListener('input', actualizarPago);
        $(id)?.addEventListener('change', actualizarPago);
    });
    document.querySelectorAll('[data-monto]').forEach((button) => {
        button.addEventListener('click', () => {
            if ($('montoRecibido')) $('montoRecibido').value = button.dataset.monto;
        });
    });
    $('btnMontoExacto')?.addEventListener('click', () => {
        if ($('montoRecibido')) $('montoRecibido').value = $('totalFinalVenta')?.value || '0.00';
    });
    formPago?.addEventListener('submit', validarPago);
    btnBuscarCliente?.addEventListener('click', consultarDocumento);
    formCliente?.addEventListener('submit', guardarCliente);
    tipoDocumento?.addEventListener('change', actualizarDocumentoCliente);
    $('modalCrearCliente')?.addEventListener('shown.bs.modal', () => $('nombreCliente')?.focus());

    actualizarDocumentoCliente();
    actualizarPago();
})();
