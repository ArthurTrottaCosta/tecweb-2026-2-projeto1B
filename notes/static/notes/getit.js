document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.autoresize').forEach((textarea) => {
    const resize = () => {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    };
    textarea.addEventListener('input', resize);
    resize();
  });

  // Alterna as cores e inclinações do Get-it sem mudar a cada recarga.
  document.querySelectorAll('.card').forEach((card, index) => {
    card.classList.add(`card-color-${index % 5 + 1}`);
    card.classList.add(`card-rotation-${index % 5 + 4}`);
  });
});
