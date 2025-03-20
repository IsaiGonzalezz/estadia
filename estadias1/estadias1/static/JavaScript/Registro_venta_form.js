
document.getElementById("btnGuardar").addEventListener("click", function (event) {
  event.preventDefault();

  // Obtener datos del formulario
  const formData = new FormData(document.getElementById("ventaForm"));
  const productoId = formData.get("id_producto");
  const cantidad = parseFloat(formData.get("id_cantidad"));
  const precioTotal = parseFloat(formData.get("precio_total"));
  //let clienteId = formData.get("id_cliente");

  //document.getElementById("hidden_cliente").value = clienteId;


  // Verificar si cantidad y precio total son números válidos
  if (isNaN(cantidad) || isNaN(precioTotal)) {
      alert("Por favor, introduce valores válidos para cantidad y precio total.");
      return;
  }

  const precioFinal = cantidad * precioTotal;

  // Obtener texto de las opciones seleccionadas
  const productoText = document.querySelector(`#id_id_producto option[value="${productoId}"]`).textContent;
  //const clienteText = document.querySelector(`#id_id_cliente option[value="${clienteId}"]`).textContent;

  // Actualizar la tabla
  const table = document.getElementById("resumenTabla");
  const newRow = table.insertRow();
  newRow.innerHTML = `
      <td>${cantidad}</td>
      <td data-id="${productoId}">${productoText}</td>
      <td>$</td>
      <td>${precioFinal.toFixed(2)}</td>

  `;

  document.getElementById("editarVentaBtn").style.display = "inline";

  // Añadir botones de edición y eliminación
  const actionsCell = newRow.insertCell(-1);
  actionsCell.innerHTML = `
      <button class="editarBtn" style="display: none;">Editar</button>
      <button class="eliminarBtn" style="display: none;">Eliminar</button>
  `;
  newRow.querySelector(".editarBtn").addEventListener("click", function () {
      editarFila(newRow);
  });
  newRow.querySelector(".eliminarBtn").addEventListener("click", function () {
      eliminarFila(newRow);
  });

  //habilitar el boton de editar
  document.getElementById('editarVentaBtn').style.display="inline"
  //habilitar el boton imprimir ticket
  document.getElementById('imprimir').style.display='inline';

  actualizarTotales(precioFinal); // Asumiendo que el IVA es del 16%

  //SE LIMPIA EL FORMULARIO
  $('#id_id_producto').val(null).trigger('change');
//  console.log(clienteId);
  document.getElementById("id_id_cantidad").value = "";
  document.getElementById("id_precio_total").value = "";

});

function actualizarTotales(subtotal) {
  // Actualizar el subtotal
  const subTotalCompra = document.getElementById("total-venta");
  const nuevoSubtotal = parseFloat(subTotalCompra.textContent) + subtotal;
  subTotalCompra.textContent = nuevoSubtotal.toFixed(2);

}

document.getElementById("editarVentaBtn").addEventListener("click", function (event) {
  event.preventDefault();
  const rows = document.querySelectorAll("#resumenTabla tr");

  rows.forEach((row, index) => {
      if (index > 0) {
          row.querySelector(".editarBtn").style.display = "inline";
          row.querySelector(".eliminarBtn").style.display = "inline";
      }
  });
  document.getElementById("editarVentaBtn").style.display = "none";

});

function editarFila(row) {
  const cantidadCell = row.cells[0];
  const productoCell = row.cells[1];
  const costoCell = row.cells[3];


  const cantidad = parseFloat(cantidadCell.textContent)
  const productoId = productoCell.getAttribute("data-id");
  const costoT = parseFloat(costoCell.textContent);

  const costo = costoT/cantidad
  // Llenar el formulario con los datos de la fila
  $('#id_id_producto').val(productoId).trigger('change');
  document.getElementById("id_id_cantidad").value = cantidad;
  document.getElementById("id_precio_total").value = costo;


  // Guardar el índice de la fila para referencia
  document.getElementById("ventaForm").setAttribute("data-editing-row-index", row.rowIndex);

  // Actualizar los totales antes de eliminar la fila
  actualizarTotales(-costoT);

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
  document.getElementById("eliminarVenta").style.display = "block";
}

document.getElementById("aceptarEliminar").addEventListener("click", function (event) {
  event.preventDefault();
  if (filaParaEliminar) {
      const precioTotalCell = filaParaEliminar.cells[3];
      const precioTotal = parseFloat(precioTotalCell.textContent);
      actualizarTotales(-precioTotal);
      filaParaEliminar.remove();
      filaParaEliminar = null;
      document.getElementById("eliminarVenta").style.display = "none";
  }
});

document.getElementById("cancelarEliminar").addEventListener("click", function (event) {
  event.preventDefault();
  filaParaEliminar = null;
  document.getElementById("eliminarVenta").style.display = "none";
});



//--*-*-*-*-**-*-*-*-*-*-*-*-*-*-*-----------******************-------------------------------->
document.getElementById("registrarVentaBtn").addEventListener("click", function (event) {
  event.preventDefault();

  const fechaCompra = document.getElementById("fecha_venta").value;
  if(fechaCompra === ""){
      alert("INGRESA LA FECHA DE LA COMPRA");
      return;
  }

  const resumenTabla = document.getElementById("resumenTabla");
  const rows = resumenTabla.getElementsByTagName("tr");
  const resumenData = [];

  for (let i = 1; i < rows.length; i++) {
      const cells = rows[i].getElementsByTagName("td");
      const rowData = {
          cantidad: cells[0].innerText,
          producto_id: cells[1].getAttribute("data-id"),
          precio_total: cells[3].innerText,
      };
      resumenData.push(rowData);
  }

  const hiddenField = document.createElement("input");
  hiddenField.type = "hidden";
  hiddenField.name = "resumen_data";
  hiddenField.value = JSON.stringify(resumenData);
  document.getElementById("ventaForm").appendChild(hiddenField);

  const fechaVenta = document.getElementById("fecha_venta").value;
  const totalVenta = document.getElementById("total-venta").textContent;
  //const clienteId = document.getElementById('hidden_cliente').value;


  const fechaField = document.createElement("input");
  fechaField.type = "hidden";
  fechaField.name = "fecha_venta";
  fechaField.value = fechaVenta;
  document.getElementById("ventaForm").appendChild(fechaField);

  const totalField = document.createElement("input");
  totalField.type = "hidden";
  totalField.name = "total_venta";
  totalField.value = totalVenta;
  document.getElementById("ventaForm").appendChild(totalField);
/*
  const clienteField = document.createElement('input');
    clienteField.type = "hidden";
    clienteField.name = "cliente_id";
    clienteField.value = clienteId;
    document.getElementById("ventaForm").appendChild(clienteField);
*/

  document.getElementById("ventaForm").submit();
});

