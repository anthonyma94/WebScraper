const getProducts = {
    async: true,
    crossDomain: true,
    url: "/api/products",
    method: "GET",
    data: {},
    success: function (response) {
        updateTable(response);
    },
    error: function (response) {
        alert(`error updating from api\n ${response}`);
    },
};

const postProducts = {
    url: "/api/products",
    method: "POST",
    data: {},
    dataType: "json",
    contentType: "application/json; charset=utf-8",
    success: function (response) {
        $.ajax(getProducts);
        console.log("success");
    },
    error: function (response) {
        alert(`Error sending from api ${response}`);
    },
};

function updateTable(response) {
    console.log(response);
    $("#tableBody").empty();
    $.each(response, function (i, product) {
        $("#tableBody").append(`
        <tr>
            <td scope="row">
                ${product["id"]}
            </td>
            <td>
                ${product["name"]}
            </td>
            <td>
                NA
            </td>
            <td>
                <a href='${product["url"]}'>Link</a>
            </td>
            <td>
            False
            </td>
        </tr>
    `);
    });
}

$("#addBtn").click(function (e) {
    e.preventDefault();
    url = $("#url").val();
    if (url == "") {
        alert("No value for URL");
        return false;
    } else {
        $(this).data("previous", $(this).html());
        $(this).html(`
        <span class='spinner-border spinner-border-sm' role='status'></span>
        <span>Adding...</span>
        `);
        request = postProducts;
        request.data = JSON.stringify({ url: url });
        console.log(request);
        $.post(request).done(() => $(this).html($(this).data("previous")));
    }
});

$.ajax(getProducts);
