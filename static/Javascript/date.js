var today = new Date();
var dd = today.getDate();
var mm = today.getMonth() + 1;
var yyyy = today.getFullYear();

if (dd < 10) {
   dd = '0' + dd;
}

if (mm < 10) {
   mm = '0' + mm;
}

today = yyyy + '-' + mm + '-' + dd;
const start = document.getElementById("start")
const end = document.getElementById("end")

start.max = today ;
end.max = today;

start.addEventListener('change', () => {
   const date1Value = start.value;
   const date2MinValue = new Date(date1Value);
   date2MinValue.setDate(date2MinValue.getDate() + 1);
   end.min = date2MinValue.toISOString().slice(0, 10);
});