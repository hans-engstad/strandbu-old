


$("#CreatePayment").on('click', function() {
    $.ajax({
        url: 'api/get_payment_id',
        data: {
            "t_booking_serialized": $('#t_booking_serialized').val()
        },
        dataType: 'json',
        success: function(data) {
            paymentID = JSON.stringify(data);
            var obj = jQuery.parseJSON(paymentID);
            paymentID = obj.paymentId;
            intitCheckout(paymentID);
        }
    });
});

var checkoutOptions = {
  checkoutKey: "test-checkout-key-5342daee79e54519a6368a728721c532", //[Required] Test or Live GUID with dashes

  paymentId : $('#payment-id').val().toString(), //[required] GUID without dashes
  containerId : "dibs-complete-checkout", //[optional] defaultValue: dibs-checkout-content
  language: "en-GB",            //[optional] defaultValue: en-GB
};
var checkout = new Dibs.Checkout(checkoutOptions);
 
//this is the event that the merchant should listen to redirect to the “payment-is-ok” page
 
checkout.on('payment-completed', function(response) {
               /*
               Response:
                              paymentId: string (GUID without dashes)
               */
               window.location = '/PaymentSuccessful';
});

































function AddCabin(){
  $('#add-cabin-form').submit();
}

function RemoveCabin(number){
  $('#remove-cabin-' + number).submit();
}

/*

var handler = StripeCheckout.configure({
  key: 'pk_test_sAnddD1C8K3Nv4QefeGpEBiS',
  image: 'https://stripe.com/img/documentation/checkout/marketplace.png',
  locale: 'no',
  name: 'Strandbu Camping',
  description: '',
  // zipCode: true,
  // billingAddress: true,
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

    if($('#late-arrival-checkbox:checked'))
    {
      $('#late-arrival-field').prop('checked', true); 
    }

    //Submit form
    document.getElementById('payment-form').submit();
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

*/

$('#accept-conditions-checkbox').change(
    function(){
        if ($(this).is(':checked')) {
            //Hide conditions-error
            $('#conditions-error').addClass('hide');
        }
    });