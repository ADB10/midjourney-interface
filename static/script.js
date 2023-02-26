var socket = io.connect();

function start_generation() {
    // Get all checked checkboxes
    const version = document.getElementById("version").querySelectorAll('input[type="checkbox"]:checked');
    const ratio = document.getElementById("ratio").querySelectorAll('input[type="checkbox"]:checked');
    socket.emit('send_data', {
        prompt: document.querySelector("#prompt textarea").value,
        version: Array.from(version).map(x => x.getAttribute('id')),
        ratio: Array.from(ratio).map(x => x.getAttribute('id')),
    });

    window.location.href = "/generate_image";
}

all_img = document.querySelectorAll(".img-click")

console.log(all_img);
CURRENT = NaN

for (let index = 0; index < all_img.length; index++) {
    all_img[index].addEventListener("click", function(event) {
        elem = event.target;
        parent = elem.parentNode;
        if (elem.classList.contains("clicked")) {
            elem.classList.remove("clicked");
            parent.classList.remove("hide-bg");
            CURRENT = NaN
        } else {
            CURRENT = index
            elem.classList.add("clicked");
            parent.classList.add("hide-bg");
        }
    })
}

document.addEventListener("keydown", function(event) {
    if (event.keyCode === 37) {
        // Left arrow key pressed
        if (CURRENT !== NaN) {
            if (CURRENT > 0) {
                all_img[CURRENT].classList.remove("clicked");
                all_img[CURRENT - 1].classList.add("clicked");
                all_img[CURRENT].parentNode.classList.remove("hide-bg");
                all_img[CURRENT - 1].parentNode.classList.add("hide-bg");
                CURRENT--;
            } else {
                all_img[0].classList.remove("clicked");
                all_img[0].parentNode.classList.remove("hide-bg");
                all_img[all_img.length - 1].classList.add("clicked");
                all_img[all_img.length - 1].parentNode.classList.add("hide-bg");
                CURRENT = all_img.length - 1;
            }
        }
    }
    if (event.keyCode === 39) {
        // Right arrow key pressed
        if (CURRENT !== NaN) {
            if (CURRENT < all_img.length - 1) {
                all_img[CURRENT].classList.remove("clicked");
                all_img[CURRENT + 1].classList.add("clicked");
                all_img[CURRENT].parentNode.classList.remove("hide-bg");
                all_img[CURRENT + 1].parentNode.classList.add("hide-bg");
                CURRENT++;
            } else {
                all_img[all_img.length - 1].classList.remove("clicked");
                all_img[all_img.length - 1].parentNode.classList.remove("hide-bg");
                all_img[0].classList.add("clicked");
                all_img[0].parentNode.classList.add("hide-bg");
                CURRENT = 0;
            }
        }
    }
    if (event.keyCode === 27) {
        // Esc key pressed
        if (CURRENT !== NaN) {
            all_img[CURRENT].classList.remove("clicked");
            all_img[CURRENT].parentNode.classList.remove("hide-bg");
            CURRENT = NaN;
        }
    }
});

socket.on('receive_image', function(data) {
    version = data.version;
    ratio = data.ratio;
    url = data.url;
    if (ratio == 'base') {
        console.log("base-" + version);
        load_img = document.getElementById("base-" + version);
    } else {
        console.log(ratio + "-" + version);
        load_img = document.getElementById(ratio + "-" + version);
    }
    console.log(load_img);
    load_img.querySelector("img").src = url;
    console.log(data);
})