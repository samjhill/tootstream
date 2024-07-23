from unittest import mock
import src
from src.tootstream.toot_parser import TootParser, find_attr, has_class, unique

def test_unique():
    sequence = [1, 2, 2, 3, 4, 4, 4, 5, 6, 6, 7]
    expected_result = [1, 2, 3, 4, 5, 6, 7]
    assert unique(sequence) == expected_result

def test_unique_with_strings():
    sequence = ['a', 'b', 'b', 'c', 'd', 'd', 'd', 'e', 'f', 'f', 'g']
    expected_result = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    assert unique(sequence) == expected_result

def test_unique_with_empty_sequence():
    sequence = []
    expected_result = []
    assert unique(sequence) == expected_result

def test_unique_with_all_same_elements():
    sequence = [1, 1, 1, 1, 1]
    expected_result = [1]
    assert unique(sequence) == expected_result

def test_emoji_shortcode_to_unicode(mocker):
    mocker.patch("src.tootstream.toot_parser.emoji.emojize", return_value="😀")
    from src.tootstream.toot_parser import emoji_shortcode_to_unicode

    result = emoji_shortcode_to_unicode(":grinning:")
    assert result == "😀"

    # Test emoji.emojize call
    src.tootstream.toot_parser.emoji.emojize.assert_called_once_with(":grinning:", use_aliases=True)

def test_emoji_unicode_to_shortcodes():
    from src.tootstream.toot_parser import emoji_unicode_to_shortcodes

    assert emoji_unicode_to_shortcodes("🙂") == ":slightly_smiling_face:"
    assert emoji_unicode_to_shortcodes("🍎🍎") == ":red_apple::red_apple:"

@mock.patch('src.tootstream.toot_parser.emoji')
def test_emoji_mock(mock_emoji):
    from src.tootstream.toot_parser import emoji_unicode_to_shortcodes

    mock_emoji.demojize.return_value = ':smile:'
    result = emoji_unicode_to_shortcodes("😀")
    mock_emoji.demojize.assert_called_with('😀')
    assert result == ':smile:'

def test_find_attr_returns_correct_value():
    attrs = [('class', 'myclass'), ('id', 'myid')]
    result = find_attr('id', attrs)
    assert result == 'myid'

def test_find_attr_returns_none_if_attribute_not_present():
    attrs = [('class', 'myclass'), ('id', 'myid')]
    result = find_attr('name', attrs)
    assert result is None

def test_find_attr_returns_none_if_attributes_list_empty():
    attrs = []
    result = find_attr('name', attrs)
    assert result is None

def test_find_attr_handles_multiple_value_for_single_attribute():
    attrs = [('class', 'myclass'), ('class', 'secondclass')]
    result = find_attr('class', attrs)
    assert result == 'myclass'  # Returns the first matched attribute

def test_has_class_found(monkeypatch):
    from src.tootstream.toot_parser import find_attr
    monkeypatch.setattr('src.tootstream.toot_parser.find_attr', lambda x,y: "test_class")
    assert has_class("test_class", []) == True

def test_has_class_not_found(monkeypatch):
    from src.tootstream.toot_parser import find_attr
    monkeypatch.setattr('src.tootstream.toot_parser.find_attr', lambda x,y: "another_class")
    assert has_class("test_class", []) == False

def test_has_class_no_attr():
    assert has_class("test_class", []) == False

def test_has_class_no_value(monkeypatch):
    from src.tootstream.toot_parser import find_attr
    monkeypatch.setattr('src.tootstream.toot_parser.find_attr', lambda x,y: None)
    assert has_class("test_class", []) == False

def test_pop_line(mocker):
    parser = TootParser()
    parser.fed = ['Hello', 'World']
    line = parser.pop_line()
    assert line == "HelloWorld"
    assert parser.fed == []

def test_handle_data(mocker):
    mocker.patch('src.tootstream.toot_parser.emoji_shortcode_to_unicode')
    mocker.patch('src.tootstream.toot_parser.emoji_unicode_to_shortcodes')
    parser = TootParser()
    parser.handle_data('data')
    assert parser.fed == ['data']

def test_parse_link(mocker):
    mocker.patch('src.tootstream.toot_parser.find_attr')
    mocker.patch('src.tootstream.toot_parser.has_class')
    parser = TootParser()
    parser.parse_link([('href', 'link')])
    assert len(parser.links) == 1

def test_parse_span(mocker):
    mocker.patch('src.tootstream.toot_parser.has_class')
    parser = TootParser()
    parser.cur_type = "link"
    parser.shorten_links = True
    parser.parse_span([("class", "invisible")])
    assert parser.hide is True

def test_handle_endtag(mocker):
    parser = TootParser()
    parser.cur_type = "link"
    parser.handle_endtag('a')
    assert parser.cur_type is None

def test_get_text(mocker):
    parser = TootParser()
    parser.fed = ['Hello']
    assert parser.get_text() == "Hello"

def test_get_links(mocker):
    parser = TootParser()
    parser.links = ['link1', 'link2']
    assert parser.get_links() == ['link1', 'link2']

def test_get_weblinks(mocker):
    unique_mock = mocker.patch('src.tootstream.toot_parser.unique', return_value=['weblink1', 'weblink2', 'link1', 'link2'])
    get_links_mock = mocker.patch('src.tootstream.toot_parser.TootParser.get_links', return_value=['link1', 'link2'])
    parser = TootParser()
    parser.weblinks = ['weblink1', 'weblink2']

    assert parser.get_weblinks() == ['weblink1', 'weblink2', 'link1', 'link2']
    unique_mock.assert_called_once_with(['weblink1', 'weblink2', 'link1', 'link2'])
    get_links_mock.assert_called_once()



