// STAR RATING
    const stars = document.querySelectorAll('.star');
    const ratingLabel = document.querySelector('.rating-label');
    const feedbackForm = document.getElementById('feedbackForm');

    let ratingData = JSON.parse(localStorage.getItem('starRatingData')) || {votes:0, total:0};
    const userRated = localStorage.getItem('userRated');

    function updateStarsDisplay(rating = 0) {
      stars.forEach(star => {
        star.style.color = (star.dataset.value <= rating) ? '#FFD700' : '#ccc';
      });
    }

    function updateLabel() {
      if(ratingData.votes === 0) {
        ratingLabel.textContent = "No votes yet";
      } else {
        const avg = (ratingData.total / ratingData.votes).toFixed(2);
        ratingLabel.textContent = `${ratingData.votes} vote(s), average rating: ${avg} / 5`;
      }
    }

    if(userRated) {
      const userRating = parseInt(userRated);
      updateStarsDisplay(userRating);
      stars.forEach(s => s.style.pointerEvents = 'none');
    }

    stars.forEach(star => {
      star.addEventListener('click', () => {
        if(localStorage.getItem('userRated')) return;
        const rating = parseInt(star.dataset.value);

        ratingData.votes += 1;
        ratingData.total += rating;
        localStorage.setItem('starRatingData', JSON.stringify(ratingData));
        localStorage.setItem('userRated', rating);

        updateStarsDisplay(rating);
        stars.forEach(s => s.style.pointerEvents = 'none');
        updateLabel();

        // Show feedback form for ratings < 3
        if(rating < 3) {
          feedbackForm.style.display = 'block';
        }
      });

      star.addEventListener('mouseover', () => {
        if(localStorage.getItem('userRated')) return;
        updateStarsDisplay(parseInt(star.dataset.value));
      });

      star.addEventListener('mouseout', () => {
        if(localStorage.getItem('userRated')) return;
        updateStarsDisplay(0);
      });
    });

    updateLabel();

    function sendFeedback() {
      const feedback = document.getElementById('feedbackText').value.trim();
      if(feedback === "") {
        alert("Please enter feedback before submitting so we can know what you want us to change!");
        return;
      }
      const mailtoLink = `mailto:jacobbrock946123@gmail.com?subject=Website Feedback&body=${encodeURIComponent(feedback)}`;
      window.location.href = mailtoLink;
    }