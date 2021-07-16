$('document').ready(function() {

    // Отправить данные на сервер из формы Создания шаблона
    document.getElementById('create_template__btn').onclick = (function(e) {
        e.preventDefault();
        let form = document.getElementById('create_template__form');
        $.ajax({
            url: '/schedule_interface/create_template/get_form/',
            data: $(form).serialize(),
            type: 'POST',
            success: function(data) {
                console.log('yeah!');
                },
            error: function() {
                console.log('error');
                }
        });
    });

});