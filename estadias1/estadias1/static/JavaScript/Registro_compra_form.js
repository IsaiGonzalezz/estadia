document.querySelectorAll("#id_cantidad, #id_costo", ".iva").forEach(function(input) {
    input.addEventListener("keypress", function(event) {
        if (event.key === "Enter" && input.type !== 'checkbox') {
            event.preventDefault(); // Prevenir el envío del formulario
        }
    });
});

document.getElementById("btnGuardar").addEventListener("click", function (event) {
    event.preventDefault();
    const formData = new FormData(document.getElementById("compraForm"));
    const productoId = formData.get("id_producto");

    let proveedorId = formData.get("id_proveedor");
    if (document.getElementById("id_id_proveedor").disabled) {
        proveedorId = document.getElementById("hidden_proveedor").value;
    } else {
        document.getElementById("hidden_proveedor").value = proveedorId;
    }

    const cantidad = parseFloat(formData.get("cantidad"));
    let costo = parseFloat(formData.get("costo"));
    const registroConIva = document.getElementById('iva').checked;

    const productoText = document.querySelector(`#id_id_producto option[value="${productoId}"]`).textContent;

    if (isNaN(cantidad) || isNaN(costo)) {
        alert("Por favor, introduce valores válidos");
        return;
    }

    let subtotal = 0.0;
    let iva = 0.0;
    let precioTotal = 0.0;

    if (registroConIva) {
        precioTotal = cantidad * costo;
        subtotal = precioTotal / 1.16;
        iva = precioTotal - subtotal;
    } else {
        subtotal = cantidad * costo;
        iva = subtotal * 0.16;
        precioTotal = subtotal + iva;
    }

    const table = document.getElementById("resumenTabla");
    const newRow = table.insertRow();
    newRow.innerHTML = `
        <td>${cantidad}</td>
        <td data-id="${productoId}">${productoText}</td>
        <td>$</td>
        <td>${costo.toFixed(2)}</td>
        <td>$</td>
        <td>${(cantidad * costo).toFixed(2)}</td>
        <td style="display:none;">${registroConIva}</td> <!-- Columna oculta para saber si el producto es registrado con IVA -->
    `;

    document.getElementById("id_id_proveedor").disabled = true;

    actualizarTotales(subtotal, iva);


    document.getElementById('registrarCompraBtn').style.display='inline';
    document.getElementById("editarCompraBtn").style.display = "inline"; // BOTÓN PARA EDITAR COMPRA, APARECE UNA VEZ QUE SE AÑADE UNA PRODUCTO A LA TABLA


    const actionsCell = newRow.insertCell(-1);
    actionsCell.innerHTML = `
        <button class="editarBtn" style="display: none;">Editar</button> 
        <button class="eliminarBtn" style="display: none;">Eliminar</button>
    `; // CREA LOS BOTONES ELIMINAR Y EDITAR DENTRO DE LA TABLA EN LA COLUMNA ACCIONES

    // SE LE AÑADEN FUNCIONES A LOS BOTONES
    newRow.querySelector(".editarBtn").addEventListener("click", function () {
        editarFila(newRow);
        document.getElementById('cambiarProveedorBtn').style.display = 'inline';
    });
    newRow.querySelector(".eliminarBtn").addEventListener("click", function () {
        eliminarFila(newRow);
    });

    // SE LIMPIA EL FORMULARIO
    $('#id_id_producto').val(null).trigger('change');
    document.getElementById("id_cantidad").value = "";
    document.getElementById("id_costo").value = "";
    document.getElementById('cambiarProveedorBtn').style.display = 'none';
});

document.getElementById("editarCompraBtn").addEventListener("click", function (event) {
    event.preventDefault();
    const rows = document.querySelectorAll("#resumenTabla tr");

    rows.forEach((row, index) => {
        if (index > 0) {
            row.querySelector(".editarBtn").style.display = "inline";
            row.querySelector(".eliminarBtn").style.display = "inline";
        }
    });
    document.getElementById("editarCompraBtn").style.display = "none";
});

function editarFila(row) {  
    const cantidadCell = row.cells[0];
    const productoCell = row.cells[1];
    const costoCell = row.cells[3];
    const subtotalCell = row.cells[5];
    const ivaCell = row.cells[6];

    const cantidad = parseFloat(cantidadCell.textContent);
    const productoid = productoCell.getAttribute("data-id");
    let costo = parseFloat(costoCell.textContent);
    const subtotalTabla = parseFloat(subtotalCell.textContent);
    const registroConIva = ivaCell.textContent === 'true';
    const iva = registroConIva ? (subtotalTabla / 1.16 * 0.16) : (subtotalTabla * 0.16);

    const subtotal = registroConIva? (subtotalTabla / 1.16) : (subtotalTabla)

    actualizarTotales(-subtotal, -iva);

    $('#id_id_producto').val(productoid).trigger('change');
    document.getElementById("id_cantidad").value = cantidad;
    document.getElementById("id_costo").value = costo.toFixed(2);
    document.getElementById("iva").checked = registroConIva;

    document.getElementById("compraForm").setAttribute("data-editing-row-index", row.rowIndex);

    eliminarFilaParaEditar(row);

    const editarButtons = document.querySelectorAll(".editarBtn");
    const eliminarButtons = document.querySelectorAll(".eliminarBtn");
    editarButtons.forEach(button => button.style.display = 'none');
    eliminarButtons.forEach(button => button.style.display = 'none');
}

function eliminarFilaParaEditar(row) {  
    row.remove();
}

function eliminarFila(row) {
    filaParaEliminar = row;
    document.getElementById("eliminarCompra").style.display = "block";
}

document.getElementById('aceptarEliminar').addEventListener('click', function (event) {
    event.preventDefault();
    if (filaParaEliminar) {
        const subtotalCell = filaParaEliminar.cells[5];
        const ivaCell = filaParaEliminar.cells[6]; // Columna oculta para IVA

        const subtotalTabla = parseFloat(subtotalCell.textContent);
        const registroConIva = ivaCell.textContent === 'true';
        const iva = registroConIva ? (subtotalTabla / 1.16 * 0.16) : (subtotalTabla * 0.16);

        const subtotal = registroConIva ? (subtotalTabla / 1.16) : (subtotalTabla)

        actualizarTotales(-subtotal, -iva);

        filaParaEliminar.remove();
        filaParaEliminar = null;
        document.getElementById("eliminarCompra").style.display = "none";
    }
});

document.getElementById('cancelarEliminar').addEventListener('click', function (event) {
    event.preventDefault();
    filaParaEliminar = null;
    document.getElementById("eliminarCompra").style.display = "none";
});

function actualizarTotales(subtotalTabla, iva) {  
    const subTotalCompra = document.getElementById('subtotal-compra');
    const nuevoSubtotal = parseFloat(subTotalCompra.textContent) + subtotalTabla;
    subTotalCompra.textContent = nuevoSubtotal.toFixed(2);

    const ivaCompra = document.getElementById('iva-compra');
    const nuevaIva = parseFloat(ivaCompra.textContent) + iva;
    ivaCompra.textContent = nuevaIva.toFixed(2);

    const totalCompra = document.getElementById("total-compra");
    const nuevoTotal = parseFloat(totalCompra.textContent) + subtotalTabla + iva;
    totalCompra.textContent = nuevoTotal.toFixed(2);
}

document.getElementById('cambiarProveedorBtn').addEventListener('click', function(event){
    event.preventDefault();
    cambiarProveedor();
})

function cambiarProveedor(){
    document.getElementById('cambiarProveedor').style.display = 'block';
    document.getElementById("cambiarProveedorBtn").style.display = "none";
}

document.getElementById('aceptarCambiar').addEventListener('click', function(event){
    event.preventDefault();
    document.getElementById('id_id_proveedor').disabled = false;
    document.getElementById('cambiarProveedor').style.display = 'none';
})

document.getElementById('cancelarCambiar').addEventListener('click', function(event){
    event.preventDefault();
    document.getElementById('cambiarProveedor').style.display = 'none';
})

document.getElementById("registrarCompraBtn").addEventListener("click", function (event) {

    event.preventDefault();


    const resumenTabla = document.getElementById("resumenTabla");
    const rows = resumenTabla.getElementsByTagName("tr");
    const resumenData = [];

    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName("td");
        const registroConIva = cells[6].textContent === 'true';
        let costoC = parseFloat(cells[3].innerText);
        
        console.log('123')

        let costo;
        if (registroConIva) {
            costo = costoC;
        } else {
            costo = costoC * 1.16;
        }
        
        console.log('456')

        const rowData = {
            cantidad: cells[0].innerText,
            producto_id: cells[1].getAttribute("data-id"),
            costo: costo,
            precio_total: cells[5].innerText,
        };
        resumenData.push(rowData);
    }
            
    const hiddenField = document.createElement("input");
    hiddenField.type = "hidden";
    hiddenField.name = "resumen_data";
    hiddenField.value = JSON.stringify(resumenData);
    document.getElementById("compraForm").appendChild(hiddenField);
    
    const fechaCompra = document.getElementById("fecha").value;
    const TotalCompra = document.getElementById('total-compra').innerText;
    const TotalCompraValor = parseFloat(TotalCompra);

    if(fechaCompra === ""){
        alert("Ingrese la fecha de la compra");
        return;
    }else if(TotalCompraValor === 0){
        alert("Ingrese una compra");
        return;
    }
    
    
    const totalCompra = document.getElementById("total-compra").textContent;
    const proveedorId = document.getElementById('hidden_proveedor').value;

    const fechaField = document.createElement("input");
    fechaField.type = "hidden";
    fechaField.name = "fecha_compra";
    fechaField.value = fechaCompra;
    document.getElementById("compraForm").appendChild(fechaField);

    const totalField = document.createElement("input");
    totalField.type = "hidden";
    totalField.name = "total_compra";
    totalField.value = totalCompra;
    document.getElementById("compraForm").appendChild(totalField);

    const proveedorField = document.createElement('input');
    proveedorField.type = "hidden";
    proveedorField.name = "proveedor_id";
    proveedorField.value = proveedorId;
    document.getElementById("compraForm").appendChild(proveedorField);

    document.getElementById("compraForm").submit();



});
