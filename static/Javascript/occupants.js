const occupants = document.getElementById("occupants");
const child = document.getElementById("children");
const teens = document.getElementById("teens");
const adults = document.getElementById("adults");
const elders = document.getElementById("elders");
const graduated = document.getElementById("graduated");
const post = document.getElementById("post");
const full = document.getElementById("full");
const part = document.getElementById("part");


full.addEventListener('change', () => {
    full.max = (isNaN(parseInt(adults.value)) ? 0 : parseInt(adults.value));
});

part.addEventListener('change', () => {
    part.max = (isNaN(parseInt(adults.value)) ? 0 : parseInt(adults.value)) - (isNaN(parseInt(full.value)) ? 0 : parseInt(full.value));
});


graduated.addEventListener('change', () => {
    graduated.max = (isNaN(parseInt(adults.value)) ? 0 : parseInt(adults.value)) +
        (isNaN(parseInt(elders.value)) ? 0 : parseInt(elders.value));
});

post.addEventListener('change', () => {
    post.max = (isNaN(parseInt(adults.value)) ? 0 : parseInt(adults.value)) +
        (isNaN(parseInt(elders.value)) ? 0 : parseInt(elders.value));
});

function auto_fill_occupants() {
    let temp = (isNaN(parseInt(child.value)) ? 0 : parseInt(child.value)) +
            (isNaN(parseInt(teens.value))   ? 0 : parseInt(teens.value)) +
            (isNaN(parseInt(adults.value)) ? 0 : parseInt(adults.value)) +
            (isNaN(parseInt(elders.value)) ? 0 : parseInt(elders.value));
    occupants.min = temp;

    occupants.max = temp;

    if (parseInt(adults.value) === 0){
        full.value = 0
        part.value = 0
    }
}