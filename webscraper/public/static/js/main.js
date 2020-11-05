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
    },
};

const deleteTasks = {
    url: "/api/tasks",
    method: "DELETE",
    success: function (response) {
        location.reload();
    },
    error: function (response) {
        console.log(response);
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
            <td>${parseFloat(product.price_limit).toFixed(2)}</td>
            <td>${product.purchase}</td>
            <td>${product.completed}</td>
            <td>
              <a href="${product.product.url}" target="_blank">Link</a>
            </td>
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

    $(this).validate();

    // data = build_data([...$(this).find(`input:not(.btn), select`)]);
    // data.notify_on_available = $("#notify_on_available").is(":checked");
    // data.purchase = $("#purchase").is(":checked");
    // // data.profile = data.purchase ? data.profile : null;
    // let request = postTasks;

    // request.data = JSON.stringify(data);
    // $.ajax(request);
});

function build_data(form) {
    data = {};

    form.forEach((item) => {
        data = { ...data, [item.name]: item.value };
    });

    return data;
}

$("form").validate({
    // debug: true,
    ignore: ".ignore",
    rules: {
        url: "url",
        price_limit: "number",
    },
    submitHandler: function (form) {
        let button = $(form).find("input[type=submit]");
        button.data("previous", $(this).html());
        button.html(`
        <span class='spinner-border spinner-border-sm' role='status'></span>
        <span>Adding...</span>
        `);
        data = build_data([...$(form).find(`input:not(.btn), select`)]);
        data.notify_on_available = $("#notify_on_available").is(":checked");
        data.purchase = $("#purchase").is(":checked");
        // data.profile = data.purchase ? data.profile : null;
        let request = postTasks;

        request.data = JSON.stringify(data);
        $.ajax(request).then(null, () => button.html(button.data("previous")));
    },
});

$(document).on("click", ".delete-button", function () {
    let request = deleteTasks;
    request.url += `/${$(this).data("id")}`;

    $.ajax(request);
});

setInterval(() => $.ajax(getTasks), 3000);

// $.ajax(getProducts);
