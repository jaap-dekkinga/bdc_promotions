/* ==========================================================================
   Be DC — site behavior
   Two things you'll want to edit before/after launch are marked TODO below.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {

  /* ---- Mobile nav toggle ---------------------------------------------- */
  var toggle = document.querySelector('.nav-toggle');
  var links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var open = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    links.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { links.classList.remove('open'); });
    });
  }

  /* ---- TODO #1: paste your Printful product links here -----------------
     Once your Printful Quick Store (or Shopify + Printful store) is live,
     copy each product's public URL in below. Any slug left as "" will show
     a "Notify me" button instead of a dead link, so the site is safe to
     launch before the store is ready.
  ------------------------------------------------------------------------- */
  var PRINTFUL_LINKS = {
    'tshirt-white': '',
    'tshirt-dark':  '',
    'hoodie':       '',
    'polo':         '',
    'hat':          '',
    'tote':         '',
    'mug':          ''
  };

  document.querySelectorAll('.product-card').forEach(function (card) {
    var slug = card.getAttribute('data-slug');
    var btn = card.querySelector('.shop-btn');
    var url = PRINTFUL_LINKS[slug];
    if (url) {
      btn.setAttribute('href', url);
      btn.setAttribute('target', '_blank');
      btn.setAttribute('rel', 'noopener');
      btn.textContent = 'Shop this design';
    } else {
      btn.setAttribute('href', '#contact');
      btn.textContent = 'Notify me';
      btn.addEventListener('click', function () {
        var msg = document.getElementById('message');
        if (msg) {
          msg.value = 'Let me know when the ' + card.getAttribute('data-name') + ' is available to order.';
        }
      });
    }
  });

  /* ---- TODO #2: contact form ---------------------------------------------
     This works out of the box with zero setup: it opens the visitor's email
     client with the message pre-filled (mailto:). If you'd rather have
     submissions land quietly in an inbox without opening Mail, sign up free
     at formspree.io, then:
       1. Change the <form> tag's action to your Formspree endpoint and
          method to "POST".
       2. Delete the submit-event listener below (the browser will handle
          the submit natively).
  ------------------------------------------------------------------------- */
  var form = document.getElementById('contact-form');
  var status = document.getElementById('form-status');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = document.getElementById('name').value.trim();
      var email = document.getElementById('email').value.trim();
      var message = document.getElementById('message').value.trim();
      if (!name || !email || !message) {
        status.textContent = 'Please fill in every field before sending.';
        return;
      }
      var subject = encodeURIComponent('Message from Be DC site — ' + name);
      var body = encodeURIComponent(message + '\n\n— ' + name + ' (' + email + ')');
      // TODO: replace with your own contact address before launch.
      window.location.href = 'mailto:bdcpromotions@gmail.com?subject=' + subject + '&body=' + body;
      status.textContent = 'Opening your email app to send this…';
    });
  }

  /* ---- Footer year ------------------------------------------------------ */
  var yearEl = document.getElementById('year');
  if (yearEl) { yearEl.textContent = new Date().getFullYear(); }
});
