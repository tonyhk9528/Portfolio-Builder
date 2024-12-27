document.addEventListener("DOMContentLoaded", (event) => {
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
  
  const resetForm = () => {
    document.querySelector('[name="name"]').value = initialData.name;
    document.querySelector('[name="location"]').value = initialData.location;
    quill.setContents(initialData.about);
  };
  
  resetForm();
  
  const form = document.querySelector('form');
  form.addEventListener('formdata', (event) => {
    // Append Quill content before submitting
    event.formData.append('about', JSON.stringify(quill.getContents().ops));
  });
  
  document.querySelector('#resetForm').addEventListener('click', () => {
    resetForm();
  });});

