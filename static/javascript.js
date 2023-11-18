function post() {
    // fetch data from form
    let comment = $('#textarea-post').val();
    // fetch today date and convert it to string
    let today = new Date().toISOString();

    $.ajax({
        type: 'POST',
        url: '/posting',
        data: {
            comment_give: comment,
            date_give: today
        },
        success: function (response) {
            // close the modal 
            $('#modal-post').removeClass('is-active')
            window.location.reload();
        }
    })
}

// Handle the long time post 
function time2str(date) {
    let today = new Date(); // day and date of today (?)
    // comparing both value today and date
    // getting the time in between
    // 1000 to second
    // 60 to minutes
    let time = (today - date) / 1000 / 60;
    //minutes
    if (time < 60) {
        return parseInt(time) + ' minutes ago'; // convert to bil bulat
    }
    time = time / 60;
    //hours
    if (time < 24) {
        return parseInt(time) + ' hours ago';
    }
    time = time / 24;
    //weeks
    if (time < 7) {
        return parseInt(time) + ' days ago';
    }
    // date.month.year
    let year = date.getFullYear();
    let month = date.getMonth() + 1;
    let day = date.getDate();
    return `${year}.${month}.${day}`;
}

// reformat the like count
function num2str(count) {
    //k
    if (count > 10000) {
        return parseInt(count / 1000) + 'k'
    }
    // decimal of k
    if (count > 500) {
        // 1000 -> 100 -> 1 + k 
        // 550 -> 5 -> 0.5 + k
        return parseInt(count / 100 / 10) + 'k'
    }
    if (count == 0) {
        return '';
    }

    return count;
}

function get_post(username) {
    if(username === undefined){
        username = '';
    }
    // target the form and empty it
    $('#post-box').empty();
    $.ajax({
        type: 'GET',
        url: `/get_posts?username_give=${username}`,
        data: {},
        success: function (response) {
            if (response['result'] === 'success') {
                let posts = response['posts'];
                for (let i = 0; i < posts.length; i++) {
                    let post = posts[i];
                    // convert the date string into date format
                    let time_post = new Date(post['date']);
                    let time_before = time2str(time_post); // time in between
                    // this is if statement
                    // before ? is the if statement
                    // after ? is the 
                    // : else
                    let class_heart = post['heart_by_me'] ? 'fa-heart' : 'fa-heart-o';
                    // if the user like postingan tersedia
                    // if not
                    let class_star = post['star_by_me'] ? 'fa-star' : 'fa-star-o';
                    let class_thumbsup = post['thumbsup_by_me'] ? 'fa-thumbs-up' : 'fa-thumbs-o-up';
                    let temp_html = `
            <div class="box" id="${post['_id']}">
              <article class="media">
                <div class="media-left">
                  <a href="/user/${post['username']}" class="image is-64x64">
                    <img src="/static/${post['profile_pic_real']}" alt="Image" class="is-rounded"/>
                  </a>
                </div>
                <div class="media-content">
                  <div class="content">
                    <p>
                      <strong>${post['profile_name']}</strong>&nbsp;<small>@${post['username']}</small>
                      &nbsp;&nbsp;|  <small>${time_before}</small>
                      <br/>
                      ${post['comment']}
                    </p>
                  </div>
                  <nav class="level is-mobile">
                    <div class="level-left">
                      <a 
                        class="level-item is-sparta"
                        aria-label="heart"
                        onclick="toggle_like('${post["_id"]}', 'heart')">
                        <span class="icon is-small">
                          <i class="fa ${class_heart}" aria-hidden="True"></i>
                        </span>&nbsp; <span class="like-num">${num2str(post['count_heart'])}</span>
                      </a>
                      <a 
                        class="level-item is-sparta"
                        aria-label="star"
                        onclick="toggle_star('${post["_id"]}', 'star')">
                        <span class="icon is-small">
                          <i class="fa ${class_star}" aria-hidden="true"></i>
                        </span>&nbsp; <span class="like-num">${num2str(post['count_star'])}</span>
                      </a>
                      <a 
                        class="level-item is-sparta"
                        aria-label="thumbsup"
                        onclick="toggle_thumbsup('${post["_id"]}', 'thumbsup')">
                        <span class="icon is-small">
                          <i class="fa ${class_thumbsup}" aria-hidden="True"></i>
                        </span>&nbsp; <span class="like-num">${num2str(post['count_thumbsup'])}</span>
                      </a>
                    </div>
                  </nav>
                </div>
              </article>
            </div>
            `;
                    $('#post-box').append(temp_html)
                    if (!post['count_heart']) {
                        console.log(`fail`)
                    }
                }
            }
        }
    })
}

function toggle_like(post_id, type) {
    let $a_like = $(`#${post_id} a[aria-label='heart']`); // targeting and set the id of each box comment
    let $i_like = $a_like.find('i'); // check whether there is i tag or not
    if ($i_like.hasClass('fa-heart')) {
        // if already has heart icon = means user want to cancel like
        $.ajax({
            type: 'POST',
            url: '/update_like',
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: 'unlike'
            },
            success: function (response) {
                // set the heart to hati-kosong
                $i_like.addClass('fa-heart-o').removeClass('fa-heart');
                // update anchor text to real total like
                // find tag span with class 'like-num'
                // then update the text
                $a_like.find('span.like-num').text(num2str(response['count']));
            }
        })
    } else {
        // if already has heart icon = means user want to cancel like
        $.ajax({
            type: 'POST',
            url: '/update_like',
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: 'like'
            },
            success: function (response) {
                // set the heart to hati-kosong
                $i_like.addClass('fa-heart').removeClass('fa-heart-o');
                // update anchor text to real total like
                // find tag span with class 'like-num'
                // then update the text
                $a_like.find('span.like-num').text(num2str(response['count']));
            }
        })
    }
}

function toggle_star(post_id, type) {
    let $a_like = $(`#${post_id} a[aria-label='star']`); // targeting and set the id of each box comment
    let $i_like = $a_like.find('i'); // check whether there is i tag or not
    if ($i_like.hasClass('fa-star')) {
        // if already has star icon = means user want to cancel like
        $.ajax({
            type: 'POST',
            url: '/update_like',
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: 'unlike'
            },
            success: function (response) {
                // set the heart to hati-kosong
                $i_like.addClass('fa-star-o').removeClass('fa-star');
                // update anchor text to real total like
                // find tag span with class 'like-num'
                // then update the text
                $a_like.find('span.like-num').text(num2str(response['count']));
            }
        })
    } else {
        // if already has star icon = means user want to cancel like
        $.ajax({
            type: 'POST',
            url: '/update_like',
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: 'like'
            },
            success: function (response) {
                // set the star to hati-kosong
                $i_like.addClass('fa-star').removeClass('fa-star-o');
                // update anchor text to real total like
                // find tag span with class 'like-num'
                // then update the text
                $a_like.find('span.like-num').text(num2str(response['count']));
            }
        })
    }
}

function toggle_thumbsup(post_id, type) {
    let $a_like = $(`#${post_id} a[aria-label='thumbsup']`); // targeting and set the id of each box comment
    let $i_like = $a_like.find('i'); // check whether there is i tag or not
    if ($i_like.hasClass('fa-thumbs-up')) {
        // if already has thumbs-up icon = means user want to cancel like
        $.ajax({
            type: 'POST',
            url: '/update_like',
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: 'unlike'
            },
            success: function (response) {
                // set the thumbs-up to hati-kosong
                $i_like.addClass('fa-thumbs-o-up').removeClass('fa-thumbs-up');
                // update anchor text to real total like
                // find tag span with class 'like-num'
                // then update the text
                $a_like.find('span.like-num').text(num2str(response['count']));
            }
        })
    } else {
        // if already has thumbs-up icon = means user want to cancel like
        $.ajax({
            type: 'POST',
            url: '/update_like',
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: 'like'
            },
            success: function (response) {
                // set the thumbs-up to hati-kosong
                $i_like.addClass('fa-thumbs-up').removeClass('fa-thumbs-o-up');
                // update anchor text to real total like
                // find tag span with class 'like-num'
                // then update the text
                $a_like.find('span.like-num').text(num2str(response['count']));
            }
        })
    }
}