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

// Portfolio scroll
document.addEventListener("DOMContentLoaded", () => {

  const navLinks = document.querySelectorAll('.port-nav-link');  
  const sections = document.querySelectorAll('section');

  let currentSection = 'about';

  window.addEventListener('scroll', () => {
    sections.forEach(section => {
      if (window.scrollY >= section.offsetTop - 80) { 
        currentSection = section.id;
      }
    });

    navLinks.forEach(navLink => {
      if (navLink.href.includes(currentSection)) {
        navLink.classList.add('active');
      } else {
        navLink.classList.remove('active');
      }
    });
  });

});

