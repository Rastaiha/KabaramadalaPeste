let data = {};

function setOffers(response, isMyOffer = false) {
  response.offers.forEach((offer) => {
    let offer_template = $('.offer-template').clone();
    let offer_item_template = $('.offer-item-template').clone();

    offer_template
      .find('.offer-user-img')
      .attr('src', offer.creator_participant_picture_url);

    offer_template
      .find('.offer-username')
      .text(offer.creator_participant_username);
    offer_template
      .find('.offer-suggested-list')
      .html("<div class='exchange-type'>+</div>");
    offer_template
      .find('.offer-requested-list')
      .html("<div class='exchange-type'>-</div>");
    for (const key in offer) {
      if (offer.hasOwnProperty(key)) {
        let property, property_type;
        if (key.startsWith('suggested_')) {
          property_type = 'suggested';
          property = key.replace('suggested_', '');
        } else if (key.startsWith('requested_')) {
          property_type = 'requested';
          property = key.replace('requested_', '');
        } else {
          continue;
        }
        if (offer[key]) {
          offer_item_template.find('.offer-item-number').text(offer[key]);
          offer_item_template
            .find('img')
            .attr('src', prop_details[property].src);
          offer_item_template
            .find('img')
            .attr('title', prop_details[property].persian);
          offer_template
            .find('.offer-' + property_type + '-list')
            .append(offer_item_template.html());
        }
      }
    }

    offer_template.find('.offer-btns a').attr('data-pk', offer.pk);

    if (isMyOffer) {
      offer_template.find('.exchange-card').removeClass('acc-offer');
      offer_template.find('.exchange-card').addClass('del-offer');
      $('.my-offers .exchanges-list').append(offer_template.html());
    } else {
      offer_template.find('.exchange-card').addClass('acc-offer');
      offer_template.find('.exchange-card').removeClass('del-offer');
      $('.all-offers .exchanges-list').append(offer_template.html());
    }
  });
}

get_player_info()
  .then((response) => {
    if (response.currently_anchored) {
      $('.back-to-island').css('display', 'inline-block');
    }
    data.username = response.username;
  })
  .then(get_all_offers)
  .then((response) => setOffers(response, false))
  .then(get_my_offers)
  .then((response) => setOffers(response, true))
  .then(() => {
    $('.offer-btns a').click(function () {
      let title = 'مبادله';
      let question = 'آیا مبادله را می‌پذیرید؟';
      let kind = 'accept';
      if ($(this).hasClass('delete-offer')) {
        title = 'حذف پیشنهاد';
        question = 'آیا می‌خواهید پیشنهاد خود را حذف کنید؟';
        kind = 'delete';
      }
      my_prompt(question, title, {
        kind: kind,
        pk: $(this).data('pk'),
      });
      $('#prompt_modal').modal('show');
    });
  })
  .catch(default_fail);
$('.last-exchanges-btn').click(function () {
  get_recent_transactions()
    .then((response) => {
      $('.last-exchanges-list').html('');
      response.offers.forEach((offer) => {
        var last_exchanges_item_template = $('.last-exchanges-item-template').clone();
        var offer_item_template = $('.offer-item-template').clone();
        last_exchanges_item_template
          .find('.last-exchanges-s .last-exchanges-item-img')
          .attr('src', offer.creator_participant_picture_url);
        last_exchanges_item_template
          .find('.last-exchanges-c .last-exchanges-item-img')
          .attr('src', offer.acceptor_participant_picture_url);

        last_exchanges_item_template
          .find('.last-exchanges-s .last-exchanges-item-username')
          .text(offer.creator_participant_username);

        last_exchanges_item_template
          .find('.last-exchanges-c .last-exchanges-item-username')
          .text(offer.acceptor_participant_username);
        for (const key in offer) {
          if (offer.hasOwnProperty(key)) {
            let property, property_type;
            if (key.startsWith('suggested_')) {
              property_type = 'suggested';
              property = key.replace('suggested_', '');
            } else if (key.startsWith('requested_')) {
              property_type = 'requested';
              property = key.replace('requested_', '');
            } else {
              continue;
            }
            if (offer[key]) {
              offer_item_template.find('.offer-item-number').text(offer[key]);
              offer_item_template
                .find('img')
                .attr('src', prop_details[property].src);
              offer_item_template
                .find('img')
                .attr('title', prop_details[property].persian);
              last_exchanges_item_template
                .find('.offer-' + property_type + '-list')
                .append(offer_item_template.html());
            }
          }
        }
        $('.last-exchanges-list').append(last_exchanges_item_template.html());
      });
    })
    .catch(default_fail);
});

$('#prompt_modal_btn').click(function () {
  if ($(this).data('kind')) {
    switch ($(this).data('kind')) {
      case 'accept':
        accept_offer($(this).data('pk'))
          .then(() => {
            my_alert('مبادله با موفقیت انجام شد.', 'مبادله');
            setTimeout(function () {
              window.location.href = '/game/exchange/';
            }, 1000);
          })
          .catch(default_fail);
        break;
      case 'delete':
        delete_offer($(this).data('pk'))
          .then(() => {
            my_alert('حذف پیشنهاد با موفقیت انجام شد.', 'حذف پیشنهاد');
            setTimeout(function () {
              window.location.href = '/game/exchange/';
            }, 1000);
          })
          .catch(default_fail);
        break;

      default:
        break;
    }
  }
});

$('#add_exchange_modal_btn').click(function () {
  create_offer($('#add_exchange_modal form'))
    .then(() => {
      my_alert('پیشنهاد شما ثبت شد.', 'پیشنهاد');
      setTimeout(function () {
        window.location.href = '/game/exchange/';
      }, 1000);
    })
    .catch(default_fail);
});
