$(function () {
  $('[data-toggle="popover"]').popover()
})


$("#payment-button").click(function(e) {

    // Fetch form to apply Bootstrap validation
    var form = $(this).parents('form');
    
    if (form[0].checkValidity() === false) {
      e.preventDefault();
      e.stopPropagation();
    }
    else {
      // Perform ajax submit here
      //form.submit();
    }
    
    form.addClass('was-validated');
});

/*var form = $('#payment-form');
var ownerInfo = {
  owner: {
    name: $('#id_name').val(),
    email: $('#id_email').val(),
    address: {
      country: $('#id_country').val(),
    }
  },
};

form.on('submit', function(event){
  event.preventDefault();
  
  stripe.createSource(card, ownerInfo).then(function(result){
    if(result.error)
    {
      // Inform the user if there was an error
      var errorElement = $('#card-error-text');
      errorElement.val(result.error.message);

      $('#card-error-container').removeClass('hide');
    }
    else
    {
      // Send the source to your server
      stripeSourceHandler(result.source);
    }
  })
});

function stripeSourceHandler(source) {
  // Insert the source ID into the form so it gets submitted to the server
  var form = document.getElementById('payment-form');
  var hiddenInput = document.createElement('input');
  hiddenInput.setAttribute('type', 'hidden');
  hiddenInput.setAttribute('name', 'stripeSource');
  hiddenInput.setAttribute('value', source.id);
  form.appendChild(hiddenInput);

  console.log("su");
  console.log(source);

  // Submit the form
  form.submit();
}

*/







var handler = StripeCheckout.configure({
  key: 'pk_test_sAnddD1C8K3Nv4QefeGpEBiS',
  image: 'https://stripe.com/img/documentation/checkout/marketplace.png',
  locale: 'auto',
  token: function(token) {
    // You can access the token ID with `token.id`.
    // Get the token ID to your server-side code for use.
  }
});

$('#payment-form').on('submit', function(e){
  e.preventDefault();
  
  // Open Checkout with further options:
  handler.open({
    name: 'Strandbu_test',
    description: '2 widgets',
    currency: 'nok',
    amount: 2000
  });
});

// Close Checkout on page navigation:
window.addEventListener('popstate', function() {
  handler.close();
});