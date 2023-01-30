from scraping_scripts import *

def main(topics=None, question_links=None, save_dir = None, previous_save_number=0, save_frequency_main=100, get_views=False):
    
    if topics is None:
        topics = []
    if question_links is None:
        topics = []

    assert type(save_dir) is str, 'save_dir should be a valid string pointing to a directory'
    assert type(topics) is list, 'topics should be a list of links'
    assert type(question_links) is list, 'question_links should be a list of links'

    if topics:
        question_links = questions(topics)
        if get_views:
            get_answers_w_views(question_links, n_save=previous_save_number, save_frequency=save_frequency_main)
        else:
            get_answers(question_links, n_save=previous_save_number, save_frequency=save_frequency_main)

    else:
        assert len(question_links > 0),  "question_links and topics can't be both empty"
        if get_views:
            get_answers_w_views(question_links, n_save=previous_save_number, save_frequency=save_frequency_main)
        else:
            get_answers(question_links, n_save=previous_save_number, save_frequency=save_frequency_main)


if __name__ == "__main__":
    main()
