$('document').ready(function() {

    // Создать нового специалиста
    // Открыть модальное окно Создания нового специалиста
    document.getElementById('open_create_person_form').onclick = (function() {
        $("#createPerson").modal();
    });

    // Отправляет форму создания специалиста на сервер
    document.getElementById('create_person__form_btn').onclick = (function(e) {
        e.preventDefault();
        let form = document.getElementById('create_person__form');

        $.ajax({
            url: '/structure/create_person/',
            data: $(form).serialize(),
            type: 'POST',
            success: function(data) {
                location.reload();
                },
            error: function() {
                console.log('error');
                }
        });
    });


    // Перевод специалиста
    // Открыть модальное окно Перевода специалиста
    document.querySelectorAll('.open_transfer_person_form').forEach(function(element) {
        element.onclick = (function(a) {
            a.preventDefault();
            let person_id = element.dataset.person_id;
            let last_team = element.dataset.person_team;
            send_transfer_person_form(person_id, last_team);
            $("#transferPerson").modal();
        });
    });

    // Отправляет форму перевода специалиста на сервер
    function send_transfer_person_form(person_id, last_team) {
        document.getElementById('transfer_person__btn').onclick = (function(e) {
            e.preventDefault();
            let form = document.getElementById('transfer_person__form');

            $.ajax({
                url: '/structure/transfer_person/',
                data: $(form).serialize() + "&person_id=" + person_id + "&last_team=" + last_team,
                type: 'POST',
                success: function(data) {
                    location.reload();
                    },
                error: function() {
                    console.log('error');
                    }
            });
        });
    }


    // Увольнение специалиста
    // Открыть модальное окно Увольнения специалиста
    document.querySelectorAll('.open_fire_person_form').forEach(function(element) {
        element.onclick = (function(a) {
            a.preventDefault();
            let person_id = element.dataset.person_id;
            send_fire_person_form(person_id);
            $("#firePerson").modal();
        });
    });

    // Отправляет форму увольнения специалиста на сервер
    function send_fire_person_form(person_id) {
        document.getElementById('fired_person__btn').onclick = (function(e) {
            e.preventDefault();
            let form = document.getElementById('fired_person__form');

            $.ajax({
                url: '/structure/fire_person/',
                data: $(form).serialize() + "&person_id=" + person_id,
                type: 'POST',
                success: function(data) {
                    location.reload();
                    },
                error: function() {
                    console.log('error');
                    }
            });
        });
    }


    // Удалить специалиста
    // Слушает нажатие кнопки удаления
    document.querySelectorAll('.remove__btn').forEach(function(element) {
        element.onclick = function(e) {
            e.preventDefault();
            person_id = element.dataset.person_id;
            remove_person(person_id);
        }
    });

    // Запрашивает подтверждение удаления специалиста, если да, то отправляет запрос на удаление в бд
    function remove_person(id) {
        if (confirm('Вы точно хотите удалить специалиста?')) {
            send_remove_to_db(id);
        } else {
            console.log('Специалисту повезло');
        }
    }

    // Отправляет запрос на сервер с целью удалить специалиста
    function send_remove_to_db(id) {
        setRequestHeader()

        $.ajax({
            url: '/structure/remove_person/',
            data: {'person_id': id},
            type: 'POST',
            success: function(data) {
                location.reload();
                },
            error: function() {
                console.log('error');
                }
        });
    }



    /***** Function to GET csrftoken from Cookie *****/
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    let csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        /* these HTTP methods do not require CSRF protection */
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    /* Function to set Request Header with `CSRFTOKEN` */
    function setRequestHeader(){
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    }

    /***** _________________ *****/

});