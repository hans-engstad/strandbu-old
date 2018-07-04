
var handler = StripeCheckout.configure({
  key: 'pk_test_sAnddD1C8K3Nv4QefeGpEBiS',
  image: 'https://stripe.com/img/documentation/checkout/marketplace.png',
  locale: 'no',
  name: 'Strandbu Camping',
  description: '',
  zipCode: true,
  billingAddress: true,
  allowRememberMe: false,
  currency: 'nok',
  amount: parseInt($('#TOTAL-PRICE').val()),
  token: function(token) {
    // You can access the token ID with `token.id`.
    // Get the token ID to your server-side code for use.

    //Set value of token input for the form
    var tokenString = JSON.stringify(token);
    $('#token').val(tokenString);

    //Set value of phone and arraving-late fields
    $('#phone-field').val($('#id_phone').val());
    $('#late-arrival-field').val($('#late-arrival-checkbox').val());

    //Submit form
    $('#payment-form').submit();
  }
});

$('#payment-button').on('click', function(e){
  //Check if conditions checkbox is ticked
  if(!$('#accept-conditions-checkbox').is(":checked"))
  {
    $('#conditions-error').removeClass('hide');
  }
  else
  {
    $('#conditions-error').addClass('hide');
  }
});

$('#info-form').on('submit', function(e){
  e.preventDefault();

  // Open Checkout with further options:
  handler.open();
});

// Close Checkout on page navigation:
window.addEventListener('popstate', function() {
  handler.close();
});