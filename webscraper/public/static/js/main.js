const getTasks = {
    async: true,
    crossDomain: true,
    url: "/api/tasks",
    method: "GET",
    success: function (response) {
        // console.log(response);
        updateTable(response);
    },
    error: function (response) {
        console.log(response.responseJSON.message);
    },
};

const postTasks = {
    url: "/api/tasks",
    method: "POST",
    data: {},
    dataType: "json",
    contentType: "application/json; charset=utf-8",
    success: function (response) {
        location.reload();

        // $.ajax(getProducts);
        console.log("success");
    },
    error: function (response) {
        let container = $("#error-container");
        container.html(response.responseJSON.message).collapse("show");

        container.on("shown.bs.collapse", () =>
            setTimeout(() => {
                container.collapse("hide");
            }, 3000)
        );
        console.log(response.responseJSON.message);
    },
};

function updateTable(response) {
    console.log(response);
    $("#tableBody").empty();
    $.each(response, function (i, product) {
        $("#tableBody").append(`
        <tr>
            <td>${product.product.name}</td>
            <td>${product.current_price}</td>
            <td>${product.price_limit}</td>
            <td>${product.purchase}</td>
            <td>
              <a href="${product.product.url}" target="_blank">Link</a>
            </td>
            <td>False</td>
            <td>
              <button
                type="button"
                data-id="${product.id}"
                class="btn btn-danger btn-sm deleteButton"
              >
                Delete
              </button>
            </td>
    `);
    });
}

$("#purchase").change(function (e) {
    let profile = $(".profile-container");
    if ($(this).is(":checked")) {
        profile.removeClass("d-none").show();
    } else {
        profile.addClass("d-none").hide();
    }
});

$(document).on("submit", "form", function (e) {
    // $("form").submit(function (e) {
    e.preventDefault();

    data = build_data([...$(this).find(`input:not(.btn), select`)]);
    data.notify_on_available = $("#notify_on_available").is(":checked");
    data.purchase = $("#purchase").is(":checked");
    // data.profile = data.purchase ? data.profile : null;
    let request = postTasks;

    request.data = JSON.stringify(data);
    $.ajax(request);
});

function build_data(form) {
    data = {};

    form.forEach((item) => {
        data = { ...data, [item.name]: item.value };
    });

    return data;
}

$.ajax(getTasks);

// $("#addBtn").click(function (e) {
//     e.preventDefault();
//     url = $("#url").val();
//     if (url == "") {
//         alert("No value for URL");
//         return false;
//     } else {
//         $(this).data("previous", $(this).html());
//         $(this).html(`
//         <span class='spinner-border spinner-border-sm' role='status'></span>
//         <span>Adding...</span>
//         `);
//         request = postTasks;
//         request.data = JSON.stringify({ url: url });
//         console.log(request);
//         $.post(request).done(() => $(this).html($(this).data("previous")));
//     }
// });

// $.ajax(getProducts);
