//Quill
document.addEventListener("DOMContentLoaded", () => {
  const quill = new Quill('#editor', {
    modules: {
      toolbar: [
        [{ header: [1, 2, false] }],
        ['bold', 'italic', 'underline'],
        ['link', 'blockquote'],
        [{ list: 'ordered' }, { list: 'bullet' }],
      ],
    },
    theme: 'snow',
  });
  
    //Sending semantic HTML to db from quill
    const aboutform = document.querySelector('#aboutform');
    aboutform.addEventListener('submit', (event) => {
      event.preventDefault();
      var myEditor = document.querySelector('#editor')
      var html = myEditor.children[0].innerHTML
      const aboutMeInput = document.querySelector('#new_about_me');
      aboutMeInput.value = html;
      aboutform.submit()
  });
  
});

//Experience
document.addEventListener("DOMContentLoaded", () =>{

  //end date is current  
  document.getElementById('check-current').addEventListener('change', function() {
    const endDateInput = document.querySelector('input[name="end_date"]');
    if (this.checked) {
        endDateInput.setAttribute("readonly", true);
        endDateInput.type = 'text';
        endDateInput.value = 'CURRENT';
    } else {
        endDateInput.setAttribute("readonly", false);
        endDateInput.type = 'month';
        endDateInput.value = '';
    }
  });
});


