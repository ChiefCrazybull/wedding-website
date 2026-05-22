
document.querySelectorAll('.custom_modal .custom_modal_body').forEach(elem=>
    document.addEventListener("click", function(event) {
        if(
            event.target.classList.contains('photo-button') ||
            event.target.classList.contains('photo-container') ||
            event.target.classList.contains('photo-overlay') ||
            event.target.classList.contains('btn')
        ){
            return;
        }
        if(elem.parentElement.getAttribute('data-show') && !elem.contains(event.target) && !elem.contains(event.target)){
            close_all_modals();
        }
    })
);


document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        close_all_modals();
    }
});

function get_iban(password){
    // IBAN feature removed

}

function show_hidden_text(button, target_id){

    let div = document.getElementById(target_id);

    if(div.getAttribute('data-show')){
        div.removeAttribute('data-show');
        button.innerHTML = 'Show More';
    } else{
        div.setAttribute('data-show', true);
        button.innerHTML = 'Show Less';
    }
}


function handleTickInit(tick) {

    var counter = Tick.count.down('2027-05-22T15:00:00-06:00');


    counter.onupdate = function(value) {
        tick.value = value;
    };
}

function setTickToSpanish(){
    var localization = {
        YEAR_PLURAL: 'Años',
        YEAR_SINGULAR: 'Año',
        MONTH_PLURAL: 'Meses',
        MONTH_SINGULAR: 'Mes',
        WEEK_PLURAL: 'Semanas',
        WEEK_SINGULAR: 'Semana',
        DAY_PLURAL: 'Días',
        DAY_SINGULAR: 'Día',
        HOUR_PLURAL: 'Horas',
        HOUR_SINGULAR: 'Hora',
        MINUTE_PLURAL: 'Minutos',
        MINUTE_SINGULAR: 'Minuto',
        SECOND_PLURAL: 'Segundos',
        SECOND_SINGULAR: 'Segundo',
        MILLISECOND_PLURAL: 'Milisegundos',
        MILLISECOND_SINGULAR: 'Milisegundo'
    };

    for (var key in localization) {
        if (!localization.hasOwnProperty(key)){continue;}
        Tick.options.setConstant(key, localization[key]);
    }
}

function set_language(idioma){
    document.getElementById('language-div').setAttribute('data-hide', true);
    document.querySelector('html').removeAttribute('data-block-scroll');
    window.scrollTo(0, 0);

    if(idioma === 'english'){
    }
}

function toggle_menu(){
    let menu = document.getElementById('menu');
    if(menu.getAttribute('data-expanded')){
        menu.removeAttribute('data-expanded');
    } else{
        menu.setAttribute('data-expanded', true);
    }
}

function close_menu(){
    menu.removeAttribute('data-expanded');
}

function open_modal(modal_id){
    document.querySelector('html').setAttribute('data-block-scroll', true);
    document.getElementById(modal_id).setAttribute('data-show', true);
}

function openScheduleModal(){
    document.getElementById('menu').removeAttribute('data-expanded');
    open_modal('todo-modal');
}

// Wire up navbar menu items via addEventListener so stopPropagation works
// (inline onclick on these divs would still bubble and trigger the document
//  click handler that closes all modals before they have a chance to render)
(function() {
    function menuNav(id, action) {
        var el = document.getElementById(id);
        if (!el) return;
        el.addEventListener('click', function(e) {
            e.stopPropagation();
            document.getElementById('menu').removeAttribute('data-expanded');
            action();
        });
    }
    menuNav('menu-item-info',     function() { document.getElementById('general-information-header').scrollIntoView({behavior:'smooth'}); });
    menuNav('menu-item-schedule', function() { open_modal('todo-modal'); });
    menuNav('menu-item-faq',      function() { document.getElementById('faq-div').scrollIntoView({behavior:'smooth'}); });
    menuNav('menu-item-registry', function() { document.getElementById('registry-div').scrollIntoView({behavior:'smooth'}); });
    menuNav('menu-item-rsvp',     function() { document.getElementById('rsvp-div').scrollIntoView({behavior:'smooth'}); });
})();


function close_all_modals(){
    document.querySelector('html').removeAttribute('data-block-scroll');
    document.querySelectorAll('.custom_modal').forEach(elem=>elem.removeAttribute('data-show'));
}

function openQrOverlay(imgSrc, label, account) {
    document.getElementById('qr-overlay-img').src = imgSrc;
    document.getElementById('qr-overlay-label').textContent = label;
    document.getElementById('qr-overlay-account').textContent = account;
    var overlay = document.getElementById('qr-overlay');
    overlay.style.opacity = '1';
    overlay.style.visibility = 'visible';
}

function closeQrOverlay() {
    var overlay = document.getElementById('qr-overlay');
    overlay.style.opacity = '0';
    overlay.style.visibility = 'hidden';
}


// ─────────────────────────────────────────────────────────────────────────────
// SPANISH VERSION
// To edit the Spanish translation, search for the section you want below.
// Each block is labelled with a comment like "── MENU ──", "── FAQS ──", etc.
// ─────────────────────────────────────────────────────────────────────────────

function set_page_to_spanish(){

    document.title = 'La Boda de Jocelyn & Ryan';

    setTickToSpanish();

    window.siteLang = 'spanish';

    // ── LOADING SCREEN TEXT ──
    document.getElementById('rsvp-loading-text').innerHTML = 'Enviando tu confirmación…<br><span style="font-size:.85em; opacity:.8;">Esto puede tardar hasta 10 segundos.</span>';

    // ── PHOTO CAROUSEL COUNTER ──
    var carouselCounter = document.getElementById('carousel-counter');
    if (carouselCounter) {
        carouselCounter.textContent = carouselCounter.textContent.replace(' of ', ' de ');
    }

    // ── COUNTDOWN DATE ──
    document.getElementById('date-div').innerHTML = '22 de Mayo, 2027';

    // ── MENU ──
    document.getElementById('menu-item-info').textContent     = 'Información General';
    document.getElementById('menu-item-schedule').textContent = 'Agenda';
    document.getElementById('menu-item-faq').textContent      = 'Preguntas Frecuentes';
    document.getElementById('menu-item-registry').textContent = 'Lista de Regalo';
    document.getElementById('menu-item-rsvp').textContent     = 'Confirmar Asistencia';
    document.getElementById('menu').setAttribute('data-esp', true);

    // ── OUR STORY BUTTON ──
    var osBtn = document.getElementById('our-story-btn');
    if (osBtn) {
        osBtn.textContent = 'Nuestra Historia';
        osBtn.href = 'our-story.html?lang=spanish';
    }

    // ── WELCOME ──
    document.getElementById('welcome-word').innerHTML = '¡Bienvenidos!';

    // ── MAIN SCHEDULE SUMMARY (homepage) ──
    document.getElementById('main-schedule-div').innerHTML = `
    <div>
        <h3>Ceremonia</h3>
        <div>Parroquia de Nuestra Señora de Fátima</div>
        <div>De Fátima 110, Sierra de Alica,</div>
        <div>98050 Zacatecas, Zacatecas, México</div>
        <br>
        <div>Empieza a las <b>3pm</b></div>
        <div>Recomendamos llegar <b>20 minutos</b> antes.</div>
    </div>
    <div>
        <h3>Recepción</h3>
        <div>FincaSanta</div>
        <div>Calle Independencia 28A, Centro</div>
        <div>98600 Guadalupe, Zacatecas, México</div>
        <br>
        <div>Empieza a las <b>5pm</b></div>
    </div>`;

    // ── GENERAL INFORMATION HEADER ──
    document.getElementById('general-information-header').innerHTML = 'Información General';

    // ── INFO CARDS (photo grid labels) ──
    document.getElementById('m11').innerHTML = 'Ceremonia';
    document.getElementById('mdetail1').innerHTML = 'Ver detalles';

    document.getElementById('m21').innerHTML = 'Recepción';
    document.getElementById('m22').innerHTML = 'FincaSanta';
    document.getElementById('mdetail2').innerHTML = 'Ver detalles';

    document.getElementById('m32').innerHTML = 'Transporte / Hoteles';
    document.getElementById('mdetail3').innerHTML = 'Ver detalles';

    document.getElementById('m42').innerHTML = 'Agenda de Eventos';
    document.getElementById('mdetail4').innerHTML = 'Ver detalles';

    // ── FAQS ──
    document.getElementById('faq-header').innerHTML = 'Preguntas Frecuentes';

    document.getElementById('f11').innerHTML = '¿Cuándo debería llegar a Zacatecas?';
    document.getElementById('f12').innerHTML = `
        Los eventos principales son el viernes por la noche y todo el sábado, así que recomendamos estar en Zacatecas al menos de viernes a domingo. Sin embargo, habrá actividades opcionales en grupo desde el miércoles por la mañana hasta el domingo por la tarde — ¡entre más tiempo puedas venir, mejor!
        <br><br>
        <button onclick="open_modal('todo-modal')" type="button" class="btn btn-light cream_button">Agenda de Eventos</button>
    `;

    document.getElementById('f21').innerHTML = '¿Habrá transporte disponible?';
    document.getElementById('f22').innerHTML = `
        Desde el Aeropuerto de Zacatecas habrá traslados en coche organizados por la familia de Joce y choferes de confianza. Si llegas a otro aeropuerto, podrás tomar un autobús a Zacatecas (moderno, limpio y seguro). Coordinaremos un servicio de coche desde la terminal de autobuses hasta tu hotel.
        <br><br>
        La Parroquia de Fátima está a poca distancia a pie de todos los hoteles en Zacatecas. Si no van manejando, contaremos con servicio de autobús después de la Misa, llevándolos de Fátima a FincaSanta (en ambas direcciones).
    `;

    document.getElementById('f31').innerHTML = '¿Cuál es el código de vestimenta?';
    document.getElementById('f32').innerHTML = `
        Se solicita atentamente vestimenta formal para nuestra celebración. Les invitamos a vestir de manera elegante, acorde con el estilo del evento y el entorno histórico.
        <br><br>
        También les pedimos tomar en cuenta que se trata de una ceremonia religiosa, por lo que agradecemos vestir de manera apropiada.
        <br><br>
        <button onclick="open_modal('dress-modal')" type="button" class="btn btn-light cream_button">Ver detalles</button>
    `;

    document.getElementById('f41').innerHTML = '¿Puedo traer acompañante?';
    document.getElementById('f42').innerHTML = `
        ¡Posiblemente! Si tu acompañante no está incluido en tu invitación, por favor contáctanos y con gusto te avisaremos si tenemos espacio disponible.
        <br><br>
        Sin embargo, si vienes soltero(a), no tengas miedo de llegar sin acompañante, porque habrá muchos solteros(as) en nuestra boda, ¡y las bodas siempre son una gran oportunidad para conocer gente nueva!
    `;

    document.getElementById('f51').innerHTML = '¿Se permiten niños?';
    document.getElementById('f52').innerHTML = `
        Les pedimos amablemente que únicamente asistan los niños incluidos en su invitación. Desafortunadamente, no podremos acomodar niños adicionales.
    `;

    document.getElementById('f61').innerHTML = '¿La celebración será al aire libre?';
    document.getElementById('f62').innerHTML = `
        La Misa será en interior. La recepción será en FincaSanta, un lugar con techo abierto, mitad interior, mitad exterior.
        <br><br>
        Durante el día probablemente hará calor (~27°C), pero por la noche casi siempre refresca (~10°C, estamos en el desierto a 2,450 m de altura).
        <br><br>
    `;

    // ── REGISTRY / GIFTS ──
    document.getElementById('registry-header').innerHTML = 'Lista de Regalo';
    document.getElementById('registry-text').innerHTML = `
        Su presencia en nuestra boda es el mejor regalo que nos pueden dar.
        <br>
        Para quienes deseen hacernos un regalo, hemos incluido las opciones disponibles a continuación.
    `;
    document.getElementById('registry-card-reg').style.order = '1';
    document.getElementById('registry-card-cash').style.order = '2';
    document.getElementById('registry-card-reception').style.order = '3';
    ['registry-card-reg-title','registry-card-cash-title','registry-card-reception-title'].forEach(function(id) {
        var el = document.getElementById(id);
        if (el) { el.style.minHeight = '2.8rem'; el.style.display = 'flex'; el.style.alignItems = 'flex-start'; el.style.justifyContent = 'center'; }
    });
    document.getElementById('registry-card-reg-title').innerHTML = 'Mesa de Regalos';
    document.getElementById('registry-card-reg-body').innerHTML = 'Explora nuestra lista de deseos en MyRegistry a continuación:';
    document.getElementById('registry-card-reg-btn').innerHTML = 'Ver Lista de Regalos';
    document.getElementById('registry-card-cash-title').innerHTML = 'Regalo en Efectivo (USD)';
    document.getElementById('registry-qr-hint').innerHTML = 'Haz clic arriba para el código QR.';
    document.getElementById('registry-card-reception-title').innerHTML = 'En la Recepción';
    document.getElementById('registry-card-reception-body').innerHTML = 'Contaremos con una mesa para recibir regalos y tarjetas.';

    // ── RSVP HEADER ──
    document.getElementById('rsvp-header').innerHTML = 'Confirmar Asistencia';

    // ── SEE YOU SOON ──
    document.getElementById('closing-text').innerHTML = '¡Nos vemos pronto!';

    // ── CEREMONY MODAL ──
    document.getElementById('cm-header').innerHTML = 'Detalles de la Ceremonia';
    document.getElementById('cm-body').innerHTML = `
        Parroquia de Nuestra Señora de Fátima
        <br>
        De Fátima 110, Sierra de Alica,
        <br>
        98050 Zacatecas, Zacatecas, México
        <br><br>
        Empieza a las <b>3pm</b>
        <br>
        Recomendamos llegar <b>20 minutos<b> antes.
    `;

    // ── RECEPTION MODAL ──
    document.getElementById('rm-header').innerHTML = 'Detalles de la Recepción';
    document.getElementById('rm-body').innerHTML = `
        FincaSanta
        <br>
        Calle Independencia 28A, Centro
        <br>
        98600 Guadalupe, Zacatecas, México
        <br><br>
        Empieza <b>1 hora después</b> de que termine la ceremonia.
        <br>
        Acaba alrededor de la <b>media noche</b>
    `;

    // ── TRAVEL / HOTELS MODAL ──
    document.getElementById('t-header').innerHTML = 'Transporte / Hoteles';
    document.getElementById('t-body').innerHTML = `
        <p style="font-size: 1.2rem; margin-bottom: 1.5rem;">
            Sabemos que viajar a Zacatecas requiere un poco de planificación, y agradecemos de todo corazón a quienes hacen el viaje para celebrar con nosotros.
        </p>
        <p style="font-size: 1.2rem; margin-bottom: 1.5rem;">
            Aquí les compartimos información útil sobre vuelos y hospedaje.
        </p>
        <div style="background-color: rgba(200, 169, 106, 0.12); border: 1px solid rgba(200, 169, 106, 0.35); border-radius: 1rem; padding: 1rem 1.2rem; margin-bottom: 1.75rem;">
            <b>Recordatorio de pasaporte:</b> Si viven fuera de México y necesitan pasaporte para viajar al país, verifiquen la fecha de vencimiento antes de reservar. Se recomienda que su pasaporte tenga al menos seis meses de vigencia.
        </div>
        <div style="background-color: rgba(200, 169, 106, 0.12); border: 1px solid rgba(200, 169, 106, 0.35); border-radius: 1rem; padding: 1rem 1.2rem; margin-bottom: 2rem;">
            <b>Sugerencia de llegada:</b> Si no viven en Zacatecas, recomendamos llegar 3–4 días antes de la boda para aclimatarse a la altitud (~2,400 m) y disfrutar más de los festejos.
        </div>
        <h4 style="margin-bottom: .8rem;">Vuelos</h4>
        <p style="font-size: 1.2rem; margin-bottom: 1.2rem;">
            Hay vuelos con conexión desde todas las ciudades de México al <b>Aeropuerto de Zacatecas (ZCL)</b>, generalmente con escala en Ciudad de México o Tijuana. También hay vuelos con conexión desde las principales ciudades de EE.UU., usualmente con escala en Ciudad de México, Dallas o Houston.
        </p>
        <p style="font-size: 1.2rem; margin-bottom: 2rem;">
            Para los invitados que lleguen al aeropuerto de Zacatecas, habrá traslados en coche organizados por la familia de Joce o choferes de confianza.
        </p>
        <p style="font-size: 1.2rem; margin-bottom: 1.2rem;">
            Para opciones de viaje más económicas, si viven fuera de México pueden volar a alguna de las siguientes ciudades y luego tomar un autobús a Zacatecas. Si viven dentro del país, también pueden tomar un autobús directamente desde su ciudad. ¡Los autobuses son seguros y modernos, los usamos todo el tiempo!
        </p>
        <div style="margin-bottom: 1.5rem;">
            <div><b>Ciudad de México</b>: ~8 horas en autobús</div>
            <div><b>Monterrey</b>: ~7 horas en autobús</div>
            <div><b>Aguascalientes</b>: ~2 horas en autobús</div>
            <div><b>León</b>: ~4 horas en autobús</div>
            <div><b>Guadalajara</b>: ~4 horas en autobús</div>
        </div>
        <p style="font-size: 1.2rem; margin-bottom: 1.2rem;">
            Si llegan a una de esas ciudades, pueden pedir un Uber desde el aeropuerto hasta la central de autobuses. Uber es ampliamente utilizado en México y ha sido muy seguro y confiable en nuestra experiencia.
        </p>
        <br>
        <h4 style="margin-bottom: .8rem;">Hoteles</h4>
        <p style="font-size: 1.2rem; margin-bottom: 1.2rem;">
            Animamos a todos nuestros invitados que no viven en Zacatecas a hospedarse en uno de los siguientes hoteles para que estemos todos juntos y el transporte sea más fácil:
        </p>
    `;

    document.getElementById('t-hotels').innerHTML = `
        <div style="text-align: center; width: 100%; max-width: 34rem; line-height: 1.9rem;">
            <div><a href="https://www.grupocaminoreal.com/quinta-real-zacatecas" target="_blank" rel="noopener noreferrer">Quinta Real</a></div>
            <div><a href="https://hotelesemporio.com/hoteles/emporio-zacatecas/" target="_blank" rel="noopener noreferrer">Hotel Emporio Zacatecas</a></div>
            <div><a href="https://www.hotelsantarita.com/" target="_blank" rel="noopener noreferrer">Hotel Santa Rita</a></div>
        </div>
    `;

    // ── FOOTER DATE ──
    document.getElementById('footer-date').innerHTML = '22 de Mayo, 2027';

    // ── DRESS CODE MODAL ──
    // To edit, update the innerHTML below.
    document.getElementById('dress-body').innerHTML = `
        Nuestra boda se llevará a cabo por la noche, y les pedimos que su vestimenta refleje el carácter elegante y festivo de la ocasión.
        <br><br>
        <div style="display: flex; flex-wrap: wrap; gap: 2rem; justify-content: center; margin-top: 1rem;">
            <div style="flex: 1; min-width: 260px; max-width: 400px; display: flex; flex-direction: column;">
                <h5 style="margin-bottom: 0.75rem;"><b>Mujeres</b></h5>
                Los vestidos de noche o jumpsuits elegantes son perfectos. ¡Mientras más color, mejor!
                <br>
                Les pedimos evitar vestir de blanco, marfil, beige (o cualquier tono similar), ya que estos colores están reservados para la novia.
                <br><br>
                <img src="./img/women_dress_code.jpg" alt="Código de vestimenta para mujeres" style="width: 100%; aspect-ratio: 800 / 398; object-fit: cover; border-radius: 8px; margin-top: 1.5rem;">
            </div>
            <div style="flex: 1; min-width: 260px; max-width: 400px; display: flex; flex-direction: column;">
                <h5 style="margin-bottom: 0.75rem;"><b>Hombres</b></h5>
                Por favor usar traje, saco o alguna otra vestimenta formal similar.
                <br><br>
                <img src="./img/men_dress_code.jpg" alt="Código de vestimenta para hombres" style="width: 100%; aspect-ratio: 800 / 398; object-fit: cover; border-radius: 8px; margin-top: auto;">
            </div>
        </div>
        <br>
        <b>Clima:</b> Durante el día probablemente hará calor (~27°C), por lo que recomendamos telas ligeras y frescas. Sin embargo, por la noche casi siempre refresca (~10°C), así que les sugerimos traer un chal o una chamarra ligera para mayor comodidad.
        <br><br>
        Si tienen alguna otra pregunta, no duden en contactarnos.
    `;

    // ── SCHEDULE OF EVENTS MODAL ──
    // To edit the Spanish schedule, update the innerHTML below.
    document.getElementById('sched-wrap').innerHTML = `
        <h3 id="todo-header" style="margin-bottom: .6rem; font-family: 'DM Serif Display', serif;">Agenda de Eventos</h3>

        <div class="sched-intro">
            <p>Organizamos algunas actividades divertidas antes y después de la boda para disfrutar juntos. ¡Todas son opcionales y todos son bienvenidos!
            <br>
            Haz clic en el botón de MAPA debajo de cualquier evento para abrirlo en Google Maps.
            </p>
        </div>

        <!-- MIÉRCOLES -->
        <div class="sched-day-section">
            <div class="sched-day-row">
                <div class="sched-day-label">
                    <div class="sched-day-name">Miércoles</div>
                    <div class="sched-day-sub">5/19</div>
                </div>
                <div class="sched-events-col">
                    <div class="sched-event-row">
                        <div class="sched-time">10 am – 12 pm</div>
                        <div>
                            <div class="sched-event-name">Carrera 5K en el Parque Guadalupe</div>
                            <div class="sched-event-note">Acompáñanos en nuestra ruta de 5 km, que recorre todo el Parque Ramón López Velarde.</div>
                            <a href="https://maps.app.goo.gl/b44B42oKHEAPjEdt6" target="_blank" rel="noopener" class="sched-map-link">📍 Mapa</a>
                        </div>
                    </div>
                    <div class="sched-event-row">
                        <div class="sched-time">1 – 5 pm</div>
                        <div>
                            <div class="sched-event-name">Mina el Edén</div>
                            <div class="sched-event-note">Recorre la histórica mina de plata y el museo mineralógico bajo la ciudad de Zacatecas.</div>
                            <a href="https://maps.app.goo.gl/kbJbN3pBEsEJLqtD7" target="_blank" rel="noopener" class="sched-map-link">📍 Mapa</a>
                        </div>
                    </div>
                    <div class="sched-event-row">
                        <div class="sched-time">6 – 8 pm</div>
                        <div>
                            <div class="sched-event-name">Taquería Local</div>
                            <div class="sched-event-note">Tacos en una taquería local de Guadalupe — uno de nuestros lugares favoritos.</div>
                            <a href="https://maps.app.goo.gl/NkjCyBotGeJUbUzy8" target="_blank" rel="noopener" class="sched-map-link">📍 Mapa</a>
                        </div>
                    </div>
                    <div class="sched-event-row">
                        <div class="sched-time">9 – 10 pm</div>
                        <div>
                            <div class="sched-event-name">Froyo en el Jardín</div>
                            <div class="sched-event-note">Froyo (el postre favorito de Joce) en la plaza principal de Guadalupe, con vista a el Convento.</div>
                            <a href="https://maps.app.goo.gl/TmdHG7h1wo5cQn7j8" target="_blank" rel="noopener" class="sched-map-link">📍 Mapa</a>
                        </div>
                    </div>
                </div>
                <div class="sched-image-col">
                    <div class="sched-img-pair">
                        <div class="sched-img-slot">
                            <img src="./img/mines.jpg" alt="Mina el Edén">
                        </div>
                        <div class="sched-img-caption">Mina el Edén</div>
                    </div>
                    <div class="sched-img-pair">
                        <div class="sched-img-slot">
                            <img src="./img/cerro_de_la_cruz.jpg" alt="Cerro de la Cruz">
                        </div>
                        <div class="sched-img-caption">Cerro de la Cruz</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- JUEVES -->
        <div class="sched-day-section">
            <div class="sched-day-row">
                <div class="sched-day-label">
                    <div class="sched-day-name">Jueves</div>
                    <div class="sched-day-sub">5/20</div>
                </div>
                <div class="sched-events-col">
                    <div class="sched-event-row">
                        <div class="sched-time">9:30 – 11 am</div>
                        <div>
                            <div class="sched-event-name">Caminata al Cerro de la Cruz</div>
                            <div class="sched-event-note">Subimos al lugar donde nos comprometimos. También pasaremos por un castillo otomano (a nosotros también nos sorprende).</div>
                            <a href="https://maps.app.goo.gl/jdbQqEt9WFArH1Ge7" target="_blank" rel="noopener" class="sched-map-link">📍 Mapa</a>
                        </div>
                    </div>
                    <div class="sched-event-row">
                        <div class="sched-time">1 – 4 pm</div>
                        <div>
                            <div class="sched-event-name">Viñedos Tierra Adentro</div>
                            <div class="sched-event-note">Tour y cata en una de las bodegas locales más premiadas. ¡Es una de nuestras actividades favoritas en Zacatecas!</div>
                            <a href="https://maps.app.goo.gl/WxQjVDUHFAQmxAoW7" target="_blank" rel="noopener" class="sched-map-link">📍 Mapa</a>
                        </div>
                    </div>
                    <div class="sched-event-row">
                        <div class="sched-time">6 – 9 pm</div>
                        <div>
                            <div class="sched-event-name">Cena en Nuevo Patio d' Villa</div>
                            <div class="sched-event-note">Cena con vista al atardecer en el nuevo restaurante del hermano de Joce, Javier.</div>
                            <a href="https://maps.app.goo.gl/XNSnnJ6LXYbJUJh98" target="_blank" rel="noopener" class="sched-map-link">📍 Mapa</a>
                        </div>
                    </div>
                    <div class="sched-event-row">
                        <div class="sched-time">9 – 10 pm</div>
                        <div>
                            <div class="sched-event-name">Tour de Leyendas de Zacatecas</div>
                            <div class="sched-event-note">Un autobús turístico nos llevará a recorrer lugares embrujados y legendarios por todo Zacatecas.</div>
                            <a href="https://maps.google.com/?q=22.775276,-102.572805" target="_blank" rel="noopener" class="sched-map-link">📍 Mapa</a>
                        </div>
                    </div>
                </div>
                <div class="sched-image-col">
                    <div class="sched-img-pair">
                        <div class="sched-img-slot">
                            <img src="./img/winery.jpeg" alt="Viñedo">
                        </div>
                        <div class="sched-img-caption">Viñedo Tierra Adentro</div>
                    </div>
                    <div class="sched-img-pair">
                        <div class="sched-img-slot">
                            <img src="./img/patio_night.jpeg" alt="Nuevo Patio d' Villa">
                        </div>
                        <div class="sched-img-caption">Nuevo Patio d' Villa</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- VIERNES -->
        <div class="sched-day-section">
            <div class="sched-day-row">
                <div class="sched-day-label">
                    <div class="sched-day-name">Viernes</div>
                    <div class="sched-day-sub">5/21</div>
                </div>
                <div class="sched-events-col">
                    <div class="sched-event-row">
                        <div class="sched-time">10 – 11:30 am</div>
                        <div>
                            <div class="sched-event-name">Desayuno en Patio d' Villa</div>
                            <div class="sched-event-note">Ven al primer restaurante de Javier y disfruta unos huevos rancheros, chilaquiles o un waffle para empezar el día.</div>
                            <a href="https://maps.app.goo.gl/knNSbjmqQevBnAq3A" target="_blank" rel="noopener" class="sched-map-link">📍 Mapa</a>
                        </div>
                    </div>
                    <div class="sched-event-row">
                        <div class="sched-time">12 – 2 pm</div>
                        <div>
                            <div class="sched-event-name">Teleférico a La Bufa</div>
                            <div class="sched-event-note">Viaje en teleférico con vistas panorámicas de Zacatecas.</div>
                            <a href="https://maps.app.goo.gl/64HUACQ4GJ1DjgKh6" target="_blank" rel="noopener" class="sched-map-link">📍 Mapa</a>
                        </div>
                    </div>
                    <div class="sched-event-row">
                        <div class="sched-time">2 – 4 pm</div>
                        <div>
                            <div class="sched-event-name">Paseo por el Centro de Zacatecas</div>
                            <div class="sched-event-note">Tienda de chocolate, catedral, museo de nacimientos, ¡y mucho más!</div>
                            <a href="https://maps.app.goo.gl/JMu1DAqEm7dsFk5L9" target="_blank" rel="noopener" class="sched-map-link">📍 Mapa</a>
                        </div>
                    </div>
                    <div class="sched-event-row">
                        <div class="sched-time">8 – 11 pm</div>
                        <div>
                            <div class="sched-event-name">Callejoneada</div>
                            <div class="sched-event-note">Música, baile, mezcal en burro y fiesta por las calles de Zacatecas.</div>
                            <a href="https://maps.app.goo.gl/ZZU12K1SqdmNDGmu6" target="_blank" rel="noopener" class="sched-map-link">📍 Mapa</a>
                        </div>
                    </div>
                </div>
                <div class="sched-image-col">
                    <div class="sched-img-pair">
                        <div class="sched-img-slot">
                            <img src="./img/zacviews.jpeg" alt="La Bufa">
                        </div>
                        <div class="sched-img-caption">La Bufa</div>
                    </div>
                    <div class="sched-img-pair">
                        <div class="sched-img-slot">
                            <img src="./img/early_Ryan_and_Joss_in_Zac.jpeg" alt="Zacatecas">
                        </div>
                        <div class="sched-img-caption">Zacatecas</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- SÁBADO -->
        <div class="sched-saturday">
            <div class="sched-sat-label">Sábado · 5/22</div>
            <div class="sched-sat-divider"></div>
            <div class="sched-sat-title">¡¡Día de la <em>Boda!!</em></div>
            <div class="sched-sat-divider"></div>
            <div class="sched-sat-label">El Gran Día</div>
        </div>

        <!-- DOMINGO -->
        <div class="sched-day-section">
            <div class="sched-day-row">
                <div class="sched-day-label">
                    <div class="sched-day-name">Domingo</div>
                    <div class="sched-day-sub">5/23</div>
                </div>
                <div class="sched-events-col">
                    <div class="sched-event-row">
                        <div class="sched-time">11 am – 1 pm</div>
                        <div>
                            <div class="sched-event-name">Brunch en Nuevo Patio d' Villa</div>
                            <div class="sched-event-note">Unos waffles y huevos finales antes de que todos regresen a casa.</div>
                            <a href="https://maps.app.goo.gl/XNSnnJ6LXYbJUJh98" target="_blank" rel="noopener" class="sched-map-link">📍 Mapa</a>
                        </div>
                    </div>
                    <div class="sched-event-row">
                        <div class="sched-time">3 pm</div>
                        <div>
                            <div class="sched-event-name">¡Buen Viaje a Todos!</div>
                            <div class="sched-event-note">¡Gracias a todos por venir a celebrar este día tan especial con nosotros!</div>
                        </div>
                    </div>
                </div>
                <div class="sched-image-col">
                    <div class="sched-img-pair">
                        <div class="sched-img-slot">
                            <img src="./img/us_at_patio.jpeg" alt="Patio">
                        </div>
                        <div class="sched-img-caption">Patio d' Villa</div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // ── RSVP FORM ──
    // To edit Spanish RSVP field labels, edit the innerHTML below.
    document.getElementById('rsvp-form').innerHTML = `
    <div class="rsvp-form-wrap">
        <div class="rsvp-field">
            <label>Nombre</label>
            <input type="text" id="rsvp-first" placeholder="Nombre">
        </div>
        <div class="rsvp-field">
            <label>Apellido</label>
            <input type="text" id="rsvp-last" placeholder="Apellido">
        </div>
        <div class="rsvp-field">
            <label>¿Asistirás?</label>
            <div class="rsvp-radio-group">
                <label><input type="radio" name="rsvp-attending" value="Yes"> Sí</label>
                <label><input type="radio" name="rsvp-attending" value="No"> No</label>
            </div>
        </div>
        <div id="rsvp-details" style="display:none;">
            <div class="rsvp-field">
                <label>País</label>
                <select id="rsvp-country" onchange="onCountryChange()">
                    <option value="">Selecciona una opción...</option>
                    <option value="México">México</option>
                    <option value="United States">Estados Unidos</option>
                    <option value="Canada">Canadá</option>
                    <option value="Other">Otro</option>
                </select>
            </div>
            <div class="rsvp-field">
                <label>Número de Teléfono</label>
                <input type="text" id="rsvp-phone" placeholder="Selecciona un país primero" oninput="formatPhone(this)">
            </div>
            <div class="rsvp-field">
                <label>Correo Electrónico</label>
                <input type="text" id="rsvp-email" placeholder="ej. tunombre@correo.com">
            </div>
            <div class="rsvp-field">
                <label>¿Alguna preferencia alimentaria?</label>
                <div class="rsvp-radio-group">
                    <label><input type="radio" name="rsvp-food" value="No"> No</label>
                    <label><input type="radio" name="rsvp-food" value="Yes"> Sí</label>
                </div>
                <div id="rsvp-food-detail" style="display:none; margin-top:.5rem;">
                    <input type="text" id="rsvp-allergies" placeholder="ej. Vegetariano, Vegano, Gluten, Mariscos">
                </div>
            </div>
            <div class="rsvp-field">
                <label>Llegada estimada</label>
                <select id="rsvp-arrival">
                    <option value="">Selecciona una opción...</option>
                    <option value="Early">¡Llego antes para disfrutar Zacatecas!</option>
                    <option value="Wednesday 5/19">Miércoles 5/19</option>
                    <option value="Thursday 5/20">Jueves 5/20</option>
                    <option value="Friday 5/21">Viernes 5/21</option>
                    <option value="Saturday 5/22">Sábado 5/22</option>
                    <option value="Local">Vivo localmente</option>
                </select>
            </div>
            <div class="rsvp-field">
                <label>Salida estimada</label>
                <select id="rsvp-departure">
                    <option value="">Selecciona una opción...</option>
                    <option value="Sunday 5/23">Domingo 5/23</option>
                    <option value="Monday 5/24">Lunes 5/24</option>
                    <option value="Staying later">¡Me quedo más para disfrutar Zacatecas!</option>
                    <option value="Local">Vivo localmente</option>
                </select>
            </div>
            <div class="rsvp-field">
                <label>¿Dónde te hospedarás?</label>
                <select id="rsvp-hotel">
                    <option value="">Selecciona una opción...</option>
                    <option value="Quinta Real">Quinta Real</option>
                    <option value="Hotel Emporio Zacatecas">Hotel Emporio Zacatecas</option>
                    <option value="Hotel Santa Rita">Hotel Santa Rita</option>
                    <option value="Own hotel / Airbnb">Hotel / Airbnb por mi cuenta</option>
                    <option value="Local">Vivo localmente</option>

                </select>
            </div>
            <div class="rsvp-field">
                <label>¿Te interesa alguna de nuestras actividades grupales?</label>
                <div class="rsvp-radio-group">
                    <label><input type="radio" name="rsvp-activities" value="No"> No</label>
                    <label><input type="radio" name="rsvp-activities" value="Yes"> Sí</label>
                </div>
                <div id="rsvp-activities-detail" style="display:none; margin-top:.5rem;">
                    <div class="rsvp-hint" style="margin-bottom:.4rem;">Selecciona las que te interesen:</div>
                    <div class="rsvp-checkbox-group">
                        <label><input type="checkbox" value="Wed: 5K in Guadaluple Park"> Mié: Carrera 5K en el Parque Guadalupe</label>
                        <label><input type="checkbox" value="Wed: Mina el Eden"> Mié: Mina el Edén</label>
                        <label><input type="checkbox" value="Wed: Taqueria Dinner"> Mié: Taquería Local</label>
                        <label><input type="checkbox" value="Wed: Froyo en el Jardín"> Mié: Froyo en el Jardín</label>
                        <label><input type="checkbox" value="Thu: Hike to Cerro de la Cruz"> Jue: Caminata al Cerro de la Cruz</label>
                        <label><input type="checkbox" value="Thu: Tierra Adentro Vineyards"> Jue: Viñedos Tierra Adentro</label>
                        <label><input type="checkbox" value="Thu: Dinner at Patio Nuevo"> Jue: Cena en Nuevo Patio d' Villa</label>
                        <label><input type="checkbox" value="Thu: Legends Tour"> Jue: Tour de Leyendas de Zacatecas</label>
                        <label><input type="checkbox" value="Fri: Breakfast at Patio d' Villa"> Vie: Desayuno en Patio d' Villa</label>
                        <label><input type="checkbox" value="Fri: Teleferico to La Bufa"> Vie: Teleférico a La Bufa</label>
                        <label><input type="checkbox" value="Fri: Downtown Zacatecas Walk"> Vie: Paseo por el Centro de Zacatecas</label>
                        <label><input type="checkbox" value="Fri: Callejoneada"> Vie: Callejoneada</label>
                        <label><input type="checkbox" value="Sun: Brunch at Patio Nuevo"> Dom: Brunch en Nuevo Patio d' Villa</label>
                    </div>
                </div>
            </div>
            <div class="rsvp-field">
                <label>¿Familiares adicionales o acompañante?</label>
                <div id="rsvp-guests-list"></div>
                <button type="button" class="rsvp-add-guest-btn" onclick="addRsvpGuest()">+ Agregar invitado</button>
                <div class="rsvp-hint">Agrega a quien venga contigo</div>
            </div>
        </div>
        <button type="button" class="rsvp-submit-btn" id="rsvp-submit-btn" onclick="submitRsvp()">Confirmar Asistencia</button>
        <div id="rsvp-message"></div>
    </div>
    `;

    // Re-bind listeners after replacing form HTML
    bindRsvpListeners();
    rsvpGuestCount = 0;

}
