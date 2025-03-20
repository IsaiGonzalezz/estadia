function editarProducto(
    id,
    nombre,
    id_categoria,
    stock,
    costo_venta,
    costo_compra,
    porcentaje_utilidad,
    punto_reorden,
    estado
) {
    $("#producto_id").val(id);
    $("#id_nombre").val(nombre);

    $("#id_id_categoria").val(id_categoria).trigger("change");
    console.log(id_categoria + "catregoria");

    $("#id_stock").val(stock);
    $("#id_costo_venta").val(costo_venta);
    $("#id_costo_compra").val(costo_compra);
    $("#id_porcentaje_utilidad").val(porcentaje_utilidad);
    $("#id_punto_reorden").val(punto_reorden);
    $("#id_estado").prop("checked", estado == 'True' || estado == 'true' || estado == '1');
    $("#submitButton").val("Actualizar");

    const formContainer = document.getElementById("form-container");
    formContainer.classList.add('clicked');
    console.log("camviocolor")
}

