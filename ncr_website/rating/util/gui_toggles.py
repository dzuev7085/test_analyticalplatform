def gui_toggles(rating_decision_obj, show_existing_scores, **kwargs):

    #####################################################
    # GUI toggles for rating committee parameter page
    #####################################################
    if rating_decision_obj:
        if rating_decision_obj.chair and rating_decision_obj.chair_confirmed:
            show_chair = True
        else:
            show_chair = False

        if rating_decision_obj.chair \
                and not rating_decision_obj.chair_confirmed:
            show_chair_unconfirmed = True
        else:
            show_chair_unconfirmed = False

        if not rating_decision_obj.has_passed_committee_date:
            show_edit_proposed = True
        else:
            show_edit_proposed = False

        if not rating_decision_obj.has_passed_committee_date:
            show_add_member = True
        else:
            show_add_member = False

        if rating_decision_obj.date_time_committee and \
                rating_decision_obj.date_time_committee_confirmed:
            show_date_confirmed = True
        else:
            show_date_confirmed = False

        if rating_decision_obj.date_time_committee and \
                not rating_decision_obj.date_time_committee_confirmed:
            show_date_unconfirmed = True
        else:
            show_date_unconfirmed = False

        if rating_decision_obj.has_passed_committee_date:
            show_committee_comments = True
        else:
            show_committee_comments = False

        rating_commmittee_controller = {
            'show_chair': show_chair,
            'show_chair_unconfirmed': show_chair_unconfirmed,
            'show_edit_proposed': show_edit_proposed,
            'show_date_confirmed': show_date_confirmed,
            'show_date_unconfirmed': show_date_unconfirmed,
            'show_committee_comments': show_committee_comments,
            'show_add_member': show_add_member,
            'show_existing_scores': show_existing_scores,

        }
    else:
        rating_commmittee_controller = {}

    try:
        if kwargs['show_rationale']:
            show_rationale = True
        else:
            show_rationale = False

        if kwargs['allow_edit']:
            allow_edit = True
        else:
            allow_edit = False
    except:  # noqa E722
        show_rationale = True
        allow_edit = True

    rating_commmittee_controller['columns'] = {
        'show_rationale': show_rationale,
        'allow_edit': allow_edit
    }

    return rating_commmittee_controller
