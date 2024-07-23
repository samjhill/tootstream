import builtins

import pytest
from colored import fg, attr

import src
from src.tootstream.toot import (
    IDS,
    blocks,
    bookmark,
    bookmarks,
    boost,
    complete,
    cprint,
    delete,
    dismiss,
    fav,
    faves,
    favthread,
    find_original_toot_id,
    follow,
    following,
    format_display_name,
    format_toot_idline,
    format_toot_nameline,
    format_user_counts,
    format_username,
    get_list_id,
    get_mastodon,
    get_media_attachments,
    get_or_input_profile,
    limit_flag,
    links,
    list_support,
    listaccounts,
    listadd,
    listcreate,
    listdestroy,
    listremove,
    listrename,
    lists,
    login,
    mentions,
    parse_config,
    printList,
    redisplay_prompt,
    register_app,
    reject,
    requests,
    rest_limit,
    rest_to_list,
    showhistory,
    showthread,
    toot_visibility,
    unblock,
    unbookmark,
    unfav,
    unfollow,
    update_prompt,
    user,
    view,
    vote,
)

from unittest import mock
from unittest.mock import ANY, MagicMock, Mock, patch, call


def test_redisplay_prompt(capsys):
    with patch("readline.get_line_buffer") as mock_get_line_buffer:
        with patch("readline.redisplay") as mock_redisplay:
            mock_get_line_buffer.return_value = "Test Line Buffer"
            redisplay_prompt()

            capture = capsys.readouterr()
            assert capture.out == "Test Line Buffer"
            mock_get_line_buffer.assert_called()
            mock_redisplay.assert_called()


def test_find_original_toot_id_non_reblog(mocker):
    mock_toot = {"id": "1234"}
    mock_IDS_module = mocker.patch("src.tootstream.toot.IDS", autospec=True)
    assert find_original_toot_id(mock_toot) == mock_IDS_module.to_local.return_value
    mock_IDS_module.to_local.assert_called_once_with("1234")


def test_find_original_toot_id_reblog(mocker):
    mock_toot = {"reblog": {"id": "5678"}}
    mock_IDS_module = mocker.patch("src.tootstream.toot.IDS", autospec=True)
    assert find_original_toot_id(mock_toot) == mock_IDS_module.to_local.return_value
    mock_IDS_module.to_local.assert_called_once_with("5678")


def test_rest_to_list():
    assert rest_to_list("a  b    c") == ["a", "b", "c"]
    assert rest_to_list("") == [""]
    assert rest_to_list("  ") == [""]
    assert rest_to_list("abcd") == ["abcd"]


def test_rest_limit_with_single_item_in_list(mocker):
    rest = "rest"
    mocker.patch("src.tootstream.toot.rest_to_list", return_value=[rest])
    limit, rest_result = rest_limit(rest)
    assert limit is None
    assert rest_result == rest


def test_rest_limit_with_multiple_items_in_list(mocker):
    rest = "rest"
    limit_val = "limit"
    rest_list = [rest, "some_value", limit_val]
    mocker.patch("src.tootstream.toot.rest_to_list", return_value=rest_list)
    limit, rest_result = rest_limit(rest)
    assert limit == limit_val
    assert rest_result == rest


def test_update_prompt_with_context():
    username = "test-user"
    context = "testing"
    profile = "test-profile"
    prompt = update_prompt(username, context, profile)
    assert prompt == "[@test-user <testing> (test-profile)]: "


def test_update_prompt_without_context():
    username = "test-user"
    context = None
    profile = "test-profile"
    prompt = update_prompt(username, context, profile)
    assert prompt == "[@test-user (test-profile)]: "


def test_list_support(mocker):
    # set up mock
    mock_mastodon = mocker.MagicMock()
    mock_cprint = mocker.patch("src.tootstream.toot.cprint")
    mock_fg = mocker.patch("src.tootstream.toot.fg")

    # test when mastodon supports lists
    mock_mastodon.verify_minimum_version.return_value = True
    assert list_support(mock_mastodon, silent=False) == True
    mock_mastodon.verify_minimum_version.assert_called_once_with("2.1.0")
    mock_cprint.assert_not_called()

    # test when mastodon doesn't support lists and silent = False
    mock_mastodon.reset_mock()
    mock_mastodon.verify_minimum_version.return_value = False
    assert list_support(mock_mastodon, silent=False) == False
    mock_mastodon.verify_minimum_version.assert_called_once_with("2.1.0")
    mock_cprint.assert_called_once_with(
        "List support is not available with this version of Mastodon", mock_fg("red")
    )

    # test when mastodon doesn't support lists and silent = True
    mock_mastodon.reset_mock()
    mock_cprint.reset_mock()
    mock_mastodon.verify_minimum_version.return_value = False
    assert list_support(mock_mastodon, silent=True) == False
    mock_mastodon.verify_minimum_version.assert_called_once_with("2.1.0")
    mock_cprint.assert_not_called()


def test_limit_flag_with_digits():
    result, remaining = limit_flag("123")
    assert result == 123
    assert remaining == "123"


def test_limit_flag_without_digits():
    result, remaining = limit_flag("abc")
    assert result == None
    assert remaining == "abc"


def test_get_media_attachments_no_media_attachments(mocker):
    mocker.patch("src.tootstream.toot.fg", return_value="magenta")
    mocker.patch("src.tootstream.toot.stylize", side_effect=lambda x, y: x)
    toot = {"sensitive": False, "media_attachments": []}
    result = get_media_attachments(toot)
    assert result == ["  media: 0"]


@patch("src.tootstream.toot.Mastodon")
def test_get_unique_userid_numeric(MastodonMock):
    mock_mast = MagicMock()
    MastodonMock.return_value = mock_mast

    from src.tootstream.toot import get_unique_userid

    assert get_unique_userid(mock_mast, "123", True) == 123


@patch("src.tootstream.toot.Mastodon")
def test_get_unique_userid_nonexistent(MastodonMock):
    mock_mast = MagicMock()
    MastodonMock.return_value = mock_mast

    from src.tootstream.toot import get_unique_userid

    mock_mast.account_search.return_value = []
    with pytest.raises(Exception):
        get_unique_userid(mock_mast, "nonexistent_user", True)


@patch("src.tootstream.toot.Mastodon")
def test_get_unique_userid_existing(MastodonMock):
    mock_mast = MagicMock()
    MastodonMock.return_value = mock_mast

    from src.tootstream.toot import get_unique_userid

    mock_mast.account_search.return_value = [{"id": 123, "acct": "username"}]
    assert get_unique_userid(mock_mast, "username", True) == 123


@patch("src.tootstream.toot.Mastodon")
def test_get_unique_userid_exact_check(MastodonMock):
    mock_mast = MagicMock()
    MastodonMock.return_value = mock_mast

    from src.tootstream.toot import get_unique_userid

    mock_mast.account_search.return_value = [
        {"id": 123, "acct": "username@mastodon.social"}
    ]
    with pytest.raises(Exception):
        get_unique_userid(mock_mast, "username", True)


def test_get_list_id_no_argument(mocker):
    """Test if Exception is raised when no argument is passed"""
    mocker.patch("src.tootstream.toot.Mastodon")
    with pytest.raises(Exception, match="List argument missing."):
        get_list_id(mocker.ANY, None)


def test_get_list_id_empty_string_argument(mocker):
    """Test if Exception is raised when empty string is passed"""
    mocker.patch("src.tootstream.toot.Mastodon")
    with pytest.raises(Exception, match="List argument missing."):
        get_list_id(mocker.ANY, "   ")


def test_get_list_id_integer_argument(mocker):
    """Test if integer ID is returned when integer is passed as string"""
    mocker.patch("src.tootstream.toot.Mastodon")
    assert get_list_id(mocker.ANY, "123") == 123


def test_get_list_id_unknown_list(mocker):
    """Test if Exception is raised when unknown list is requested"""
    mastodon_instance = mocker.MagicMock()
    mastodon_instance.lists.return_value = [{"title": "list1", "id": 123}]
    mocker.patch("src.tootstream.toot.Mastodon", return_value=mastodon_instance)
    with pytest.raises(Exception, match="List 'unknown_list' is not found."):
        get_list_id(mastodon_instance, "unknown_list")


def test_get_list_id_known_list(mocker):
    """Test if correct list ID is returned for known list"""
    mastodon_instance = mocker.MagicMock()
    mastodon_instance.lists.return_value = [{"title": "known_list", "id": 456}]
    mocker.patch("src.tootstream.toot.Mastodon", return_value=mastodon_instance)
    assert get_list_id(mastodon_instance, "known_list") == 456


@patch("src.tootstream.toot.Mastodon")
def test_toot_visibility_with_flag_visibility(mastodon_mock):
    mastodon_instance = mastodon_mock.return_value
    mastodon_instance.account_verify_credentials.return_value = {
        "source": {"privacy": "public"}
    }

    visibility = toot_visibility(mastodon_instance, "private", "public")
    assert visibility == "private"


@patch("src.tootstream.toot.Mastodon")
def test_toot_visibility_with_parent_visibility(mastodon_mock):
    mastodon_instance = mastodon_mock.return_value
    mastodon_instance.account_verify_credentials.return_value = {
        "source": {"privacy": "public"}
    }

    visibility = toot_visibility(mastodon_instance, None, "private")
    assert visibility == "private"


@patch("src.tootstream.toot.Mastodon")
def test_toot_visibility_with_default_visibility(mastodon_mock):
    mastodon_instance = mastodon_mock.return_value
    mastodon_instance.account_verify_credentials.return_value = {
        "source": {"privacy": "public"}
    }

    visibility = toot_visibility(mastodon_instance, None, "public")
    assert visibility == "public"


@patch("src.tootstream.toot.Mastodon")
def test_toot_visibility_with_parent_public(mastodon_mock):
    mastodon_instance = mastodon_mock.return_value
    mastodon_instance.account_verify_credentials.return_value = {
        "source": {"privacy": "private"}
    }

    visibility = toot_visibility(mastodon_instance, None, "public")
    assert visibility == "private"


def test_complete_state_greater_than_length():
    with mock.patch("src.tootstream.toot.complete") as mock_complete:
        completion_list = ["hello", "help", "hip"]
        text = "he"
        state = 5
        mock_complete.return_value = None
        src.tootstream.toot.completion_list = completion_list

        assert complete(text, state) == None


def test_complete_no_matching_options():
    with mock.patch("src.tootstream.toot.complete") as mock_complete:
        completion_list = ["hello", "help", "hip"]
        text = "xyz"
        state = 0
        mock_complete.return_value = None
        src.tootstream.toot.completion_list = completion_list

        assert complete(text, state) == None


@patch("os.path.isfile", return_value=False)
@patch("configparser.ConfigParser")
def test_parse_config_not_existing_file(mock_config, mock_os):
    filename = "test.ini"
    config = parse_config(filename)

    mock_os.assert_called_with(filename)
    mock_config.assert_called()
    assert config == mock_config.return_value


def test_register_app(mocker):
    # Create a mock object for Mastodon class.
    mock_mastodon = mocker.patch("src.tootstream.toot.Mastodon")

    instance = "testinstance.com"

    # Execute function with the mocked dependency.
    result = register_app(instance)

    # Assert that the mock method got called with right arguments.
    mock_mastodon.create_app.assert_called_once_with(
        "tootstream",
        scopes=["read", "write", "follow"],
        api_base_url="https://" + instance,
    )

    # Assert that function returns what the mock returns
    assert result == mock_mastodon.create_app.return_value


def test_login_success():
    """
    Tests the login function when the login is successful.
    """
    instance = "instance"
    client_id = "id"
    client_secret = "secret"
    code = "code"

    # Mock the Mastodon object
    mastodon_mock = MagicMock()
    mastodon_mock.auth_request_url.return_value = "url"
    mastodon_mock.log_in.return_value = "token"

    with patch(
        "src.tootstream.toot.Mastodon", return_value=mastodon_mock
    ) as mastodon_constructor, patch(
        "builtins.input", return_value=code
    ) as input_mock, patch(
        "builtins.print"
    ) as print_mock:

        assert login(instance, client_id, client_secret) == "token"

        # Make sure Mastodon was created correctly
        mastodon_constructor.assert_called_once_with(
            client_id=client_id,
            client_secret=client_secret,
            api_base_url="https://" + instance,
        )

        # assert the correct print calls were made
        print_mock.assert_any_call("Click the link to authorize login.")
        print_mock.assert_any_call("url")
        print_mock.assert_any_call()

        # assert input was called correctly
        input_mock.assert_called_once_with("Enter the code you received >")

        # assert we authenticated with the correct code and scopes
        mastodon_mock.log_in.assert_called_once_with(
            code=code, scopes=["read", "write", "follow"]
        )


def test_login_fail():
    """
    Tests the login function when the login fails.
    """
    instance = "instance"
    client_id = "id"
    client_secret = "secret"
    code = "code"

    # Mock the Mastodon object
    mastodon_mock = MagicMock()
    mastodon_mock.auth_request_url.return_value = "url"
    mastodon_mock.log_in.side_effect = Exception("Failed to log in")

    with patch(
        "src.tootstream.toot.Mastodon", return_value=mastodon_mock
    ) as mastodon_constructor, patch(
        "builtins.input", return_value=code
    ) as input_mock, patch(
        "builtins.print"
    ) as print_mock:

        with pytest.raises(Exception, match="Failed to log in"):
            login(instance, client_id, client_secret)


def test_get_or_input_profile(mocker):
    instance_value = "instance"

    mocker.patch(
        "src.tootstream.toot.register_app", return_value=("client_id", "client_secret")
    )
    mocker.patch("src.tootstream.toot.cprint")
    mocker.patch("src.tootstream.toot.login", return_value="token")

    # mocker is used to mock input as well
    mocker.patch("builtins.input", return_value=instance_value)

    config = mocker.MagicMock()
    config.has_section.return_value = False

    instance, client_id, client_secret, token = get_or_input_profile(config, "profile")

    assert instance == instance_value
    assert client_id == "client_id"
    assert client_secret == "client_secret"
    assert token == "token"


def test_get_or_input_profile_with_config(mocker):
    mocker.patch("src.tootstream.toot.cprint")

    config = mocker.MagicMock()
    config.has_section.return_value = True
    config.__getitem__.return_value = {
        "instance": "instance",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "token": "token",
    }

    instance, client_id, client_secret, token = get_or_input_profile(config, "profile")

    assert instance == "instance"
    assert client_id == "client_id"
    assert client_secret == "client_secret"
    assert token == "token"


@patch("src.tootstream.toot.stylize")
@patch("src.tootstream.toot.print")
def test_cprint(mock_print, mock_stylize):
    # Given
    text_mock = "testing text"
    style_mock = "color"
    end = "\n"

    # When
    cprint(text_mock, style_mock, end)

    # Then
    mock_stylize.assert_called_once_with(text_mock, style_mock)
    mock_print.assert_called_once_with(mock_stylize.return_value, end=end)


def test_format_username_with_locked_account(mocker):
    mocker.patch.dict("src.tootstream.toot.GLYPHS", {"locked": "🔒"})
    result = format_username({"acct": "test_account", "locked": True})
    assert result == "@test_account 🔒"


def test_format_username_with_unlocked_account(mocker):
    mocker.patch.dict("src.tootstream.toot.GLYPHS", {"locked": "🔒"})
    result = format_username({"acct": "test_account", "locked": False})
    assert result == "@test_account"


def test_format_user_counts():
    mock_user = {"statuses_count": 50, "following_count": 30, "followers_count": 100}
    result = format_user_counts(mock_user)
    GLYPHS = {"toots": "📪", "following": "👣", "followed_by": "🐾"}
    expected_result = "{} :{} {} :{} {} :{}".format(
        GLYPHS["toots"],
        mock_user["statuses_count"],
        GLYPHS["following"],
        mock_user["following_count"],
        GLYPHS["followed_by"],
        mock_user["followers_count"],
    )

    assert result == expected_result


def test_format_display_name_without_convert_emoji_to_shortcode():
    assert format_display_name("emoji") == "emoji"


def test_printUser(mocker):
    # Mocking the external functions used in `printUser`
    mocker.patch("src.tootstream.toot.format_user_counts")
    mocker.patch("src.tootstream.toot.format_username")
    mocker.patch("src.tootstream.toot.format_display_name")
    mocker.patch("src.tootstream.toot.stylize")
    mocker.patch("src.tootstream.toot.cprint")
    mocker.patch("src.tootstream.toot.fg")

    # Mocking `print`
    mock_print = mocker.patch("builtins.print")

    # Mocking `re.sub`
    mock_re = mocker.patch("re.sub")

    user = {"display_name": "TestUser", "url": "testurl", "note": "testnote"}

    from src.tootstream.toot import printUser

    printUser(user)

    # Checks if all the mocked methods are called with correct parameters
    src.tootstream.toot.format_user_counts.assert_called_once_with(user)
    src.tootstream.toot.format_username.assert_called_once_with(user)
    src.tootstream.toot.format_display_name.assert_called_once_with(
        user["display_name"]
    )
    src.tootstream.toot.stylize.assert_called_once()
    src.tootstream.toot.cprint.assert_called()
    src.tootstream.toot.fg.assert_called()
    mock_print.assert_called()
    mock_re.assert_called_once_with("<[^<]+?>", "", user["note"])


@patch("src.tootstream.toot.fg")
@patch("src.tootstream.toot.format_time")
@patch("src.tootstream.toot.format_username")
@patch("src.tootstream.toot.format_display_name")
@patch("src.tootstream.toot.stylize")
def test_format_toot_nameline(
    mock_stylize,
    mock_format_display_name,
    mock_format_username,
    mock_format_time,
    mock_fg,
):
    toot = {
        "created_at": "2021-07-01T12:34:56Z",
        "account": {"display_name": "Test User", "username": "testuser"},
    }
    mock_format_time.return_value = "12:34 PM"
    mock_format_display_name.return_value = "Test User"
    mock_format_username.return_value = "testuser"
    mock_stylize.side_effect = lambda x, y: x
    mock_fg.return_value = "green"

    result = format_toot_nameline(toot, "")

    assert result == "Test User testuser 12:34 PM"


def test_format_toot_nameline_empty_toot():
    assert format_toot_nameline(None, "") == ""


def test_format_toot_idline_empty(mocker):
    mocker.patch("src.tootstream.toot.stylize", return_value="")

    assert format_toot_idline({}) == ""


def test_edittoot_with_streaming_disabled_edited_message(mocker):
    global is_streaming
    is_streaming = False
    mocker.patch("click.edit", return_value="edited_message")
    from src.tootstream.toot import edittoot

    assert edittoot("test") == "edited_message"


def test_edittoot_with_streaming_disabled_no_edited_message(mocker):
    global is_streaming
    is_streaming = False
    mocker.patch("click.edit", return_value=None)
    from src.tootstream.toot import edittoot

    assert edittoot("test") == ""


@patch("src.tootstream.toot.cprint")
def test_print_list(mock_cprint):
    # Arrange
    list_item = {"title": "Test Title", "id": "12345"}

    # Act
    printList(list_item)

    # Assert
    calls = [
        call(list_item["title"], fg("cyan"), end=" "),
        call("(id: %s)" % list_item["id"], fg("red")),
    ]
    mock_cprint.assert_has_calls(calls)


@pytest.fixture
def mastodon():
    return MagicMock()


def test_vote(mocker):
    mastodon_mock = mocker.MagicMock()
    global_ids = mocker.patch("src.tootstream.toot.IDS.to_global")
    rest_to_list_mock = mocker.patch("src.tootstream.toot.rest_to_list")

    toot_id = "23"
    rest = "1"

    global_ids.return_value = toot_id

    # Mocking rest_to_list to return a list of integers
    rest_to_list_mock.return_value = [int(rest)]

    # Mocking mastodon.status to return a dictionary
    mastodon_mock.status.return_value = {"poll": {"id": 123, "multiple": False}}

    # run function
    vote(mastodon_mock, f"{toot_id} {rest}")
    mastodon_mock.status.assert_called_once_with(toot_id)
    mastodon_mock.poll_vote.assert_called_once_with(123, [1])


def test_vote_no_poll(mocker):
    mastodon_mock = mocker.MagicMock()
    global_ids = mocker.patch("src.tootstream.toot.IDS.to_global")

    toot_id = "23"
    rest = "1"

    global_ids.return_value = toot_id

    # Mocking mastodon.status to return a dictionary with no poll
    mastodon_mock.status.return_value = {"poll": None}

    # run function
    vote(mastodon_mock, f"{toot_id} {rest}")

    mastodon_mock.status.assert_called_once_with(toot_id)
    mastodon_mock.poll_vote.assert_not_called()


def test_vote_too_many_votes(mocker):
    mastodon_mock = mocker.MagicMock()
    global_ids = mocker.patch("src.tootstream.toot.IDS.to_global")

    toot_id = "23"
    rest = "1,2,3"

    global_ids.return_value = toot_id

    # Mocking mastodon.status to return a dictionary with a poll which doesn't accept multiple votes
    mastodon_mock.status.return_value = {"poll": {"id": 123, "multiple": False}}

    # run function
    vote(mastodon_mock, f"{toot_id} {rest}")

    mastodon_mock.status.assert_called_once_with(toot_id)
    mastodon_mock.poll_vote.assert_not_called()


def test_vote_exception(mocker):
    mastodon_mock = mocker.MagicMock()
    global_ids = mocker.patch("src.tootstream.toot.IDS.to_global")

    toot_id = "23"
    rest = "1"

    global_ids.return_value = toot_id

    # Mocking exception
    mastodon_mock.status.side_effect = Exception("Test exception")

    # run function
    vote(mastodon_mock, f"{toot_id} {rest}")

    mastodon_mock.status.assert_called_once_with(toot_id)
    mastodon_mock.poll_vote.assert_not_called()


@patch("src.tootstream.toot.IDS")
@patch("src.tootstream.toot.print")
def test_delete_when_rest_is_not_none(mock_print, mock_IDS):
    mock_IDS.to_global.return_value = "global_id"
    mock_mastodon = Mock()

    delete(mock_mastodon, "rest")

    mock_IDS.to_global.assert_called_once_with("rest")
    mock_mastodon.status_delete.assert_called_once_with("global_id")
    mock_print.assert_called_once_with("Poof! It's gone.")


@pytest.mark.parametrize("rest", [None, ""])
@patch("src.tootstream.toot.IDS")
@patch("src.tootstream.toot.print")
def test_delete_when_rest_is_none_or_empty(mock_print, mock_IDS, rest):
    mock_IDS.to_global.return_value = None
    mock_mastodon = Mock()

    delete(mock_mastodon, rest)

    mock_IDS.to_global.assert_called_once_with(rest)
    mock_mastodon.status_delete.assert_not_called()
    mock_print.assert_not_called()


@patch("src.tootstream.toot.IDS", autospec=True)
@patch("src.tootstream.toot.get_content", autospec=True)
@patch("src.tootstream.toot.cprint", autospec=True)
@patch("src.tootstream.toot.fg", autospec=True)
@patch("src.tootstream.toot.attr", autospec=True)
def test_boost_success(mock_attr, mock_fg, mock_cprint, mock_get_content, mock_IDS):
    mastodon = Mock()
    toot_id = "12345"
    mock_IDS.to_global.return_value = toot_id
    mock_get_content.return_value = "some content"

    boost(mastodon, toot_id)

    mastodon.status_reblog.assert_called_once_with(toot_id)
    mastodon.status.assert_called_once_with(toot_id)
    mock_IDS.to_global.assert_called_once_with(toot_id)
    mock_cprint.assert_called()


@patch("src.tootstream.toot.IDS", autospec=True)
def test_boost_invalid_to_global(mock_IDS):
    mastodon = Mock()
    toot_id = "12345"
    mock_IDS.to_global.return_value = None

    boost(mastodon, toot_id)

    mastodon.status_reblog.assert_not_called()
    mastodon.status.assert_not_called()
    mock_IDS.to_global.assert_called_once_with(toot_id)


@patch("src.tootstream.toot.cprint", autospec=True)
@patch("src.tootstream.toot.IDS", autospec=True)
def test_boost_exception(mock_IDS, mock_cprint):
    mastodon = Mock()
    toot_id = "12345"
    mastodon.status_reblog.side_effect = Exception("Error!")
    mock_IDS.to_global.return_value = toot_id

    boost(mastodon, toot_id)

    mastodon.status_reblog.assert_called_once_with(toot_id)
    mastodon.status.assert_not_called()
    mock_IDS.to_global.assert_called_once_with(toot_id)
    mock_cprint.assert_called()


def test_unboost():
    from src.tootstream.toot import unboost
    from unittest.mock import Mock, patch

    mastodon = Mock()
    mastodon.status_unreblog.return_value = None
    mastodon.status.return_value = "unboosted_status"
    rest = Mock()

    with patch("src.tootstream.toot.IDS.to_global") as to_global_mock, patch(
        "src.tootstream.toot.get_content", return_value="boost_content"
    ) as get_content_mock, patch("src.tootstream.toot.cprint") as cprint_mock:

        to_global_mock.return_value = rest
        unboost(mastodon, rest)

        to_global_mock.assert_called_once_with(rest)
        mastodon.status_unreblog.assert_called_once_with(rest)
        mastodon.status.assert_called_once_with(rest)
        get_content_mock.assert_called_once_with("unboosted_status")
        cprint_mock.assert_called_once_with(
            "  Removed boost:\n boost_content", attr("dim")
        )


def test_unboost_with_none_rest():
    from src.tootstream.toot import unboost
    from unittest.mock import Mock, patch

    mastodon = Mock()
    rest = None

    with patch("src.tootstream.toot.IDS.to_global") as to_global_mock:
        to_global_mock.return_value = rest
        result = unboost(mastodon, rest)

        to_global_mock.assert_called_once_with(rest)
        mastodon.status_unreblog.assert_not_called()
        mastodon.status.assert_not_called()

        assert result is None


def test_fav_single_id(mocker):
    mastodon_mock = mocker.Mock()
    mastodon_mock.status_favourite.return_value = "MockedFavourite"
    mocker.patch("src.tootstream.toot.IDS.to_global", return_value=1)
    mocker.patch("src.tootstream.toot.get_content", return_value="Mocked get_content")
    mocker.patch("src.tootstream.toot.cprint")
    result = fav(mastodon_mock, "1")
    assert mastodon_mock.status_favourite.call_count == 1
    assert mastodon_mock.status_favourite.call_args_list[0][0][0] == 1


def test_fav_multiple_ids(mocker):
    mastodon_mock = mocker.Mock()
    mastodon_mock.status_favourite.return_value = "MockedFavourite"
    mocker.patch("src.tootstream.toot.IDS.to_global", side_effect=[1, 2, 3])
    mocker.patch("src.tootstream.toot.get_content", return_value="Mocked get_content")
    mocker.patch("src.tootstream.toot.cprint")
    mocker.patch("builtins.print")
    result = fav(mastodon_mock, "1,2,3")
    assert mastodon_mock.status_favourite.call_count == 3
    assert mastodon_mock.status_favourite.call_args_list[0][0][0] == 1
    assert mastodon_mock.status_favourite.call_args_list[1][0][0] == 2
    assert mastodon_mock.status_favourite.call_args_list[2][0][0] == 3


@patch("src.tootstream.toot.get_content")
@patch("src.tootstream.toot.cprint")
@patch("src.tootstream.toot.IDS")
@patch("src.tootstream.toot.rest_to_list")
def test_unfav_single(rest_to_list, IDS, cprint, get_content):
    # Given
    mastodon = MagicMock()
    mastodon.status_unfavourite.return_value = "unfaved"
    IDS.to_global.side_effect = ["global_id"]
    get_content.return_value = "unfaved_content"
    rest_to_list.return_value = ["fav_id"]

    # When
    unfav(mastodon, "rest")

    # Then
    cprint.assert_called_with(
        "  Removed favorite (fav_id):\nunfaved_content", fg("yellow")
    )
    get_content.assert_called_with("unfaved")
    IDS.to_global.assert_called_with("fav_id")
    mastodon.status_unfavourite.assert_called_with("global_id")


@patch("src.tootstream.toot.get_content")
@patch("src.tootstream.toot.cprint")
@patch("src.tootstream.toot.IDS")
@patch("src.tootstream.toot.rest_to_list")
def test_unfav_multiple(rest_to_list, IDS, cprint, get_content):
    # Given
    mastodon = MagicMock()
    mastodon.status_unfavourite.return_value = "unfaved"
    IDS.to_global.side_effect = ["global_id_1", "global_id_2"]
    get_content.return_value = "unfaved_content"
    rest_to_list.return_value = ["fav_id_1", "fav_id_2"]

    # When
    unfav(mastodon, "rest")

    # Then
    assert cprint.call_count == 2
    get_content.assert_called_with("unfaved")
    IDS.to_global.assert_any_call("fav_id_1")
    IDS.to_global.assert_any_call("fav_id_2")
    mastodon.status_unfavourite.assert_any_call("global_id_1")
    mastodon.status_unfavourite.assert_any_call("global_id_2")


def test_bookmark_existing_id(mocker):
    mastodon = mocker.Mock()
    mocker.patch("src.tootstream.toot.IDS.to_global", return_value=123)
    mocker.patch("src.tootstream.toot.get_content", return_value="Bookmark")
    bookmark(mastodon, 123)
    mastodon.status_bookmark.assert_called_once_with(123)
    mastodon.status.assert_called_once_with(123)


def test_bookmark_non_existing_id(mocker):
    mastodon = mocker.Mock()
    mocker.patch("src.tootstream.toot.IDS.to_global", return_value=None)
    bookmark(mastodon, 0)
    mastodon.status_bookmark.assert_not_called()
    mastodon.status.assert_not_called()


def test_unbookmark(mocker):
    # Create mock object for Mastodon, IDS and get_content
    mock_mastodon = mocker.Mock()
    mock_ids = mocker.patch("src.tootstream.toot.IDS")
    mock_get_content = mocker.patch("src.tootstream.toot.get_content")

    # Specify the return_values of to_global and get_content methods
    mock_ids.to_global.return_value = 10
    mock_get_content.return_value = "Test content"

    # Call the function with the mocks
    unbookmark(mock_mastodon, 5)

    # Assert that Mastodon's status_unbookmark has been called with correct argument
    mock_mastodon.status_unbookmark.assert_called_once_with(10)

    # Assert that Mastodon's status method has been called
    mock_mastodon.status.assert_called_once_with(10)

    # Assert that get_content has been called
    mock_get_content.assert_called_once()


def test_unbookmark_none(mocker):
    # Create mock object for Mastodon and IDS
    mock_mastodon = mocker.Mock()
    mock_ids = mocker.patch("src.tootstream.toot.IDS")

    # Specify the return_value of to_global method as None
    mock_ids.to_global.return_value = None

    # Call the function with the mocks
    unbookmark(mock_mastodon, 5)

    # Assert that Mastodon's status_unbookmark hasn't been called
    mock_mastodon.status_unbookmark.assert_not_called()

    # Assert that Mastodon's status method hasn't been called
    mock_mastodon.status.assert_not_called()


def test_favthread(mocker):
    rest = 23
    mock_mastodon = mocker.MagicMock()
    mock_IDS = mocker.patch("src.tootstream.toot.IDS")
    mock_IDS.to_global.return_value = rest
    mock_IDS.to_local.side_effect = lambda x: x  # Return same id
    ancestor_mock = mocker.MagicMock()
    ancestor_mock.id = 1
    descendant_mock = mocker.MagicMock()
    descendant_mock.id = 3
    mock_mastodon.status_context.return_value = {
        "ancestors": [ancestor_mock],
        "descendants": [descendant_mock],
    }

    mock_get_content = mocker.patch("src.tootstream.toot.get_content")
    mock_cprint = mocker.patch("src.tootstream.toot.cprint")

    favthread(mock_mastodon, rest)
    mock_IDS.to_global.assert_called_once_with(rest)
    mock_mastodon.status_context.assert_called_once_with(rest)
    mock_mastodon.status_favourite.assert_has_calls(
        [mocker.call(1), mocker.call(rest), mocker.call(3)]
    )
    mock_cprint.assert_has_calls(
        [
            mocker.call(
                f"  Favorited ({mock_IDS.to_local(i)}):\n"
                + mock_get_content(mock_mastodon.status_favourite(i)),
                attr("dim"),
            )
            for i in [1, rest, 3]
        ]
    )


def test_showhistory(mocker):
    mock_mastodon = mocker.MagicMock()
    mock_rest = mocker.MagicMock()
    mock_history = mocker.patch("src.tootstream.toot.history")

    showhistory(mock_mastodon, mock_rest)

    mock_history.assert_called_once_with(mock_mastodon, mock_rest, show_toot=True)


def test_showthread(mocker):
    # Create mock objects
    mock_mastodon = mocker.Mock()
    mock_rest = mocker.Mock()

    # Mock the 'thread' function
    mocker.patch("src.tootstream.toot.thread")

    # Call the function with mock objects
    showthread(mock_mastodon, mock_rest)

    # Validate that 'thread' function was called with correct parameters
    src.tootstream.toot.thread.assert_called_once_with(
        mock_mastodon, mock_rest, show_toot=True
    )


@pytest.mark.parametrize("args, expected", [("test", None), ("23", 23)])
def test_links_parse_id(args, expected):
    IDS.to_global = MagicMock(return_value=expected)
    links(None, args)
    IDS.to_global.assert_called_once_with(args)


def test_links_invalid_id():
    IDS.to_global = MagicMock(return_value=None)
    result = links(None, "test")
    assert result is None


@patch("src.tootstream.toot.toot_parser")
def test_links_get_content(mock_toot_parser):
    status_id = 23
    IDS.to_global = MagicMock(return_value=status_id)
    mocked_mastodon = MagicMock()
    mocked_toot = {"content": "test", "media_attachments": []}
    mocked_mastodon.status = MagicMock(return_value=mocked_toot)
    links(mocked_mastodon, "23")
    mock_toot_parser.parse.assert_called_once_with(mocked_toot["content"])


@pytest.fixture
def get_local_timeline(mastodon_obj):
    return mastodon_obj.timeline_local


@patch("src.tootstream.toot.note")
def test_mentions(mock_note):
    mastodon = "mock_mastodon_instance"
    rest = "mock_rest_instance"

    mentions(mastodon, rest)

    # Test if note was called with correct arguments
    mock_note.assert_called_once_with(mastodon, "-bfFpru")


def test_dismiss_all():
    mastodon = Mock()
    result = dismiss(mastodon, "")
    mastodon.notifications_clear.assert_called_once()
    mastodon.notifications_dismiss.assert_not_called()


def test_dismiss_single():
    mastodon = Mock()
    rest = "1234567"
    result = dismiss(mastodon, rest)
    mastodon.notifications_dismiss.assert_called_once_with("1234567")


def test_dismiss_list():
    mastodon = Mock()
    rest = "1234567 890123"
    result = dismiss(mastodon, rest)
    calls = [call("1234567"), call("890123")]
    mastodon.notifications_dismiss.assert_has_calls(calls)


def test_dismiss_rest_none():
    mastodon = Mock()
    rest = None
    result = dismiss(mastodon, rest)
    mastodon.notifications_clear.assert_not_called()
    mastodon.notifications_dismiss.assert_not_called()


@patch("src.tootstream.toot.get_unique_userid")
@patch("src.tootstream.toot.cprint")
def test_unblock(mock_cprint, mock_get_unique_userid):
    mock_mastodon = MagicMock()
    mock_rest = MagicMock()
    mock_get_unique_userid.return_value = 1111
    mock_mastodon.account_unblock.return_value = {"blocking": False}
    mock_mastodon.account.return_value = {"acct": "testing_account"}
    unblock(mock_mastodon, mock_rest)
    mock_get_unique_userid.assert_called_with(mock_mastodon, mock_rest)
    mock_mastodon.account_unblock.assert_called_with(1111)
    mock_cprint.assert_called_with(
        "  user 1111 is now unblocked",
        "",
    )


@patch("src.tootstream.toot.bisect")
@patch("src.tootstream.toot.get_unique_userid")
@patch("src.tootstream.toot.cprint")
def test_unblock_completion_list(mock_cprint, mock_get_unique_userid, mock_bisect):
    mock_mastodon = MagicMock()
    mock_rest = MagicMock()
    mock_get_unique_userid.return_value = 2222
    mock_mastodon.account_unblock.return_value = {"blocking": False}
    mock_mastodon.account.return_value = {"acct": "testing_account"}
    with patch(
        "src.tootstream.toot.completion_list", new_callable=MagicMock
    ) as mock_completion_list:
        mock_completion_list.__contains__.return_value = False
        unblock(mock_mastodon, mock_rest)
        mock_bisect.insort.assert_called_with(
            mock_completion_list, "@" + mock_mastodon.account.return_value["acct"]
        )


@pytest.fixture
def mastodon():
    return Mock()


@pytest.fixture
def rest():
    return "23"


def test_follow(mastodon, rest):
    with patch("src.tootstream.toot.get_unique_userid") as mock_get_unique_userid:
        mock_get_unique_userid.return_value = rest
        with patch("src.tootstream.toot.bisect") as mock_bisect:
            with patch("src.tootstream.toot.cprint") as mock_cprint:
                with patch("src.tootstream.toot.fg") as mock_fg:
                    with patch(
                        "src.tootstream.toot.completion_list", new=[]
                    ) as mock_completion_list:

                        mastodon.account_follow.return_value = {"following": True}
                        mastodon.account.return_value = {"acct": rest}

                        follow(mastodon, rest)

                        assert mock_get_unique_userid.called
                        assert mock_cprint.called
                        mock_bisect.insort.assert_called_with(
                            mock_completion_list, f"@{rest}"
                        )


def test_follow_not_following(mastodon, rest):
    with patch("src.tootstream.toot.get_unique_userid") as mock_get_unique_userid:
        mock_get_unique_userid.return_value = rest
        with patch("src.tootstream.toot.bisect") as mock_bisect:
            with patch("src.tootstream.toot.cprint") as mock_cprint:
                with patch("src.tootstream.toot.fg") as mock_fg:
                    with patch(
                        "src.tootstream.toot.completion_list", new=[]
                    ) as mock_completion_list:

                        mastodon.account_follow.return_value = {"following": False}

                        follow(mastodon, rest)

                        assert mock_get_unique_userid.called
                        mock_cprint.assert_not_called()
                        mock_fg.assert_not_called()
                        assert rest not in mock_completion_list
                        mock_bisect.insort.assert_not_called()


@patch("src.tootstream.toot.get_unique_userid")
@patch("src.tootstream.toot.cprint")
def test_unfollows_id(mock_cprint, mock_get_unique_userid):
    mock_mastodon = Mock()
    mock_mastodon.account_unfollow.return_value = {"following": False}
    mock_mastodon.account.return_value = {"acct": "test"}
    mock_get_unique_userid.return_value = 1
    unfollow(mock_mastodon, "23")
    mock_cprint.assert_called_once_with("  user 1 is now unfollowed", fg("blue"))


@patch("src.tootstream.toot.get_unique_userid")
@patch("src.tootstream.toot.cprint")
def test_unfollows_username(mock_cprint, mock_get_unique_userid):
    mock_mastodon = Mock()
    mock_mastodon.account_unfollow.return_value = {"following": False}
    mock_mastodon.account.return_value = {"acct": "test"}
    mock_get_unique_userid.return_value = 1
    unfollow(mock_mastodon, "@user@instance.example.com")
    mock_cprint.assert_called_once_with("  user 1 is now unfollowed", fg("blue"))


@patch("src.tootstream.toot.get_unique_userid")
def test_unfollows_and_removes_from_completion_list(mock_get_unique_userid):
    mock_mastodon = Mock()
    mock_mastodon.account_unfollow.return_value = {"following": False}
    mock_mastodon.account.return_value = {"acct": "test"}
    mock_get_unique_userid.return_value = 1
    completion_list = ["@test", "@other"]
    src.tootstream.toot.completion_list = completion_list
    unfollow(mock_mastodon, "@test@instance.example.com")
    assert "@test" not in completion_list


@patch("src.tootstream.toot.get_unique_userid")
def test_unfollows_and_does_not_remove_from_other_list(mock_get_unique_userid):
    mock_mastodon = Mock()
    mock_mastodon.account_unfollow.return_value = {"following": False}
    mock_mastodon.account.return_value = {"acct": "test"}
    mock_get_unique_userid.return_value = 1
    completion_list = ["@other"]
    src.tootstream.toot.completion_list = completion_list
    unfollow(mock_mastodon, "@test@instance.example.com")
    assert "@other" in completion_list


@patch("src.tootstream.toot.get_unique_userid")
@patch("src.tootstream.toot.printUser")
def test_user(mock_printUser, mock_get_unique_userid):
    mastodon = MagicMock()
    rest = "test_user"
    mock_get_unique_userid.return_value = "unique_id"

    user(mastodon, rest)
    mock_get_unique_userid.assert_called_once_with(mastodon, rest, exact=False)
    mastodon.account.assert_called_once_with("unique_id")
    mock_printUser.assert_called_once()


@patch("src.tootstream.toot.get_unique_userid")
@patch("src.tootstream.toot.printUser")
def test_user_no_profile(mock_printUser, mock_get_unique_userid):
    mastodon = MagicMock()
    rest = "test_user"
    mock_get_unique_userid.return_value = "unique_id"
    mastodon.account.return_value = None

    with pytest.raises(Exception) as err:
        user(mastodon, rest)
    assert str(err.value) == "user {rest} not found"
    mock_get_unique_userid.assert_called_once_with(mastodon, rest, exact=False)
    mastodon.account.assert_called_once_with("unique_id")


@patch("src.tootstream.toot.get_unique_userid")
@patch("src.tootstream.toot.print_toots")
def test_view_no_count(mock_print_toots, mock_get_unique_userid):
    user = "@user"
    mastodon = MagicMock()
    mastodon.account_statuses = MagicMock()
    mock_get_unique_userid.return_value = 123456

    view(mastodon=mastodon, rest=user)

    mock_get_unique_userid.assert_called_once_with(mastodon, user, exact=False)
    mastodon.account_statuses.assert_called_once_with(123456, limit=None)
    mock_print_toots.assert_called_once_with(
        mastodon,
        mastodon.account_statuses.return_value,
        ctx_name=f"{user} timeline",
        add_completion=False,
    )


@patch("src.tootstream.toot.get_unique_userid")
@patch("src.tootstream.toot.print_toots")
def test_view_with_count(mock_print_toots, mock_get_unique_userid):
    user = "@user"
    mastodon = MagicMock()
    mastodon.account_statuses = MagicMock()
    count = 10
    mock_get_unique_userid.return_value = 123456

    view(mastodon=mastodon, rest=f"{user} {count}")

    mock_get_unique_userid.assert_called_once_with(mastodon, user, exact=False)
    mastodon.account_statuses.assert_called_once_with(123456, limit=count)
    mock_print_toots.assert_called_once_with(
        mastodon,
        mastodon.account_statuses.return_value,
        ctx_name=f"{user} timeline",
        add_completion=False,
    )


def test_info(mocker):
    mastodon_mock = mocker.MagicMock()
    user_mock = mocker.MagicMock()
    mastodon_mock.account_verify_credentials.return_value = user_mock
    rest_mock = mocker.MagicMock()

    mocker.patch("src.tootstream.toot.printUser")

    import src.tootstream.toot as toot

    toot.info(mastodon_mock, rest_mock)

    mastodon_mock.account_verify_credentials.assert_called_once()
    toot.printUser.assert_called_once_with(user_mock)


def test_limit_flag():
    result = limit_flag("20")
    assert result == (20, "20")


@patch("src.tootstream.toot.limit_flag")
@patch("src.tootstream.toot.cprint")
def test_following_no_users(mock_cprint, mock_limit_flag):
    mastodon = Mock()
    mastodon.account_verify_credentials.return_value = {"id": 1}
    mastodon.fetch_remaining.return_value = []
    mock_limit_flag.return_value = (10, [])

    following(mastodon, [])

    mock_cprint.assert_called_with("  You aren't following anyone", mock.ANY)
    mastodon.fetch_remaining.assert_called()


@patch("src.tootstream.toot.limit_flag")
@patch("src.tootstream.toot.cprint")
@patch("src.tootstream.toot.printUsersShort")
def test_following_has_users(mock_printUsersShort, mock_cprint, mock_limit_flag):
    mastodon = Mock()
    mastodon.account_verify_credentials.return_value = {"id": 1}
    mastodon.fetch_remaining.return_value = [{"id": 2}, {"id": 3}, {"id": 4}]
    mock_limit_flag.return_value = (10, [])

    following(mastodon, [])

    mock_cprint.assert_called_with("  People you follow (3):", mock.ANY)
    mock_printUsersShort.assert_called()
    mastodon.fetch_remaining.assert_called()


def test_blocks_no_users(mocker):
    # Mock mastodon and rest
    mock_mastodon = mocker.Mock()
    mock_rest = mocker.Mock()
    mock_limit_flag = mocker.patch(
        "src.tootstream.toot.limit_flag", return_value=(20, mock_rest)
    )
    mock_cprint = mocker.patch("src.tootstream.toot.cprint")

    # Mock the result for no users
    mock_mastodon.fetch_remaining.return_value = []

    blocks(mock_mastodon, mock_rest)

    mock_mastodon.fetch_remaining.assert_called_once_with(
        mock_mastodon.blocks(limit=20)
    )
    mock_cprint.assert_called_once_with(
        "  You haven't blocked anyone (... yet)", mocker.ANY
    )


def test_blocks_with_users(mocker):
    # Mock mastodon and rest
    mock_mastodon = mocker.Mock()
    mock_rest = mocker.Mock()
    mock_limit_flag = mocker.patch(
        "src.tootstream.toot.limit_flag", return_value=(20, mock_rest)
    )
    mock_cprint = mocker.patch("src.tootstream.toot.cprint")
    mock_printUsersShort = mocker.patch("src.tootstream.toot.printUsersShort")

    # Mock the result for some users
    users = [mocker.Mock() for _ in range(5)]
    mock_mastodon.fetch_remaining.return_value = users

    blocks(mock_mastodon, mock_rest)

    mock_mastodon.fetch_remaining.assert_called_once_with(
        mock_mastodon.blocks(limit=20)
    )
    mock_cprint.assert_called_once_with("  You have blocked:", mocker.ANY)
    mock_printUsersShort.assert_called_once_with(users)


def test_mutes():
    from unittest.mock import Mock, patch
    from src.tootstream.toot import mutes

    with patch("src.tootstream.toot.limit_flag") as mock_limit_flag:
        with patch("src.tootstream.toot.cprint") as mock_cprint:
            with patch("src.tootstream.toot.printUsersShort") as mock_printUsersShort:
                mastodon = Mock()
                rest = ["some", "args"]
                mastodon.mutes = Mock()
                mastodon.fetch_remaining = Mock(return_value=[])
                mock_limit_flag.return_value = (10, rest)

                mutes(mastodon, rest)

                mock_limit_flag.assert_called()
                mastodon.mutes.assert_called_with(limit=10)
                mastodon.fetch_remaining.assert_called_with(mastodon.mutes(limit=10))
                mock_cprint.assert_called_with(
                    "  You haven't muted anyone (... yet)", fg("red")
                )

                users = ["user1", "user2"]
                mastodon.fetch_remaining = Mock(return_value=users)
                mutes(mastodon, rest)

                mock_cprint.assert_called_with("  You have muted:", fg("magenta"))
                mock_printUsersShort.assert_called_with(users)


@patch("src.tootstream.toot.cprint")
@patch("src.tootstream.toot.printUsersShort")
def test_requests_no_incoming(mock_printUsersShort, mock_cprint):
    mastodon = MagicMock()
    mastodon.fetch_remaining.return_value = []

    requests(mastodon, None)

    mastodon.fetch_remaining.assert_called_once()
    mock_cprint.assert_called_once_with("  You have no incoming requests", fg("red"))
    mock_printUsersShort.assert_not_called()


@patch("src.tootstream.toot.cprint")
@patch("src.tootstream.toot.printUsersShort")
def test_requests_incoming(mock_printUsersShort, mock_cprint):
    mastodon = MagicMock()
    mastodon.fetch_remaining.return_value = ["user1", "user2"]

    requests(mastodon, None)

    mastodon.fetch_remaining.assert_called_once()

    cprint_calls = [
        call("  These users want to follow you:", fg("magenta")),
        call("  run 'accept <id>' to accept", fg("magenta")),
        call("   or 'reject <id>' to reject", fg("magenta")),
    ]
    mock_cprint.assert_has_calls(cprint_calls, any_order=False)
    mock_printUsersShort.assert_called_once_with(["user1", "user2"])


def test_accept(mocker):
    # Mocking the instance method get_unique_userid
    mocker.patch("src.tootstream.toot.get_unique_userid", return_value="123")
    # Mocking the instance method follow_request_authorize
    mocker.patch("src.tootstream.toot.Mastodon.follow_request_authorize")
    # Mocking the cprint function
    mocker.patch("src.tootstream.toot.cprint")
    mastodon_mock = mocker.Mock()
    rest = "user@instance.example.com"

    from src.tootstream.toot import accept

    accept(mastodon_mock, rest)

    # Validate that the get_unique_userid was called
    src.tootstream.toot.get_unique_userid.assert_called_once_with(mastodon_mock, rest)
    # Validate that the follow_request_authorize was called
    mastodon_mock.follow_request_authorize.assert_called_once_with("123")
    # Validate that the cprint was called
    src.tootstream.toot.cprint.assert_called_once_with(
        "  user user@instance.example.com's follow request is accepted", mocker.ANY
    )


def test_reject(mocker):
    # Mocking instances
    mocked_mastodon = mocker.MagicMock()
    rest = "@user@instance.example.com"

    # Mocking methods
    mocker.patch("src.tootstream.toot.get_unique_userid", return_value="123")
    mocker.patch("src.tootstream.toot.cprint")
    mocker.patch("src.tootstream.toot.fg")

    # Calling the function
    reject(mocked_mastodon, rest)

    # Asserts
    src.tootstream.toot.get_unique_userid.assert_called_once_with(mocked_mastodon, rest)
    mocked_mastodon.follow_request_reject.assert_called_once_with("123")
    src.tootstream.toot.cprint.assert_called_once_with(
        "  user @user@instance.example.com's follow request is rejected",
        src.tootstream.toot.fg("blue"),
    )


@patch("src.tootstream.toot.print_toots")
def test_faves(mock_print_toots):
    mock_mastodon = Mock()

    # setup the return value for favourites
    favourite_toots = ["favourite toot 1", "favourite toot 2"]
    mock_mastodon.favourites.return_value = favourite_toots

    # call the function
    faves(mock_mastodon, "rest")

    # validate that print_toots was called with correct parameters
    mock_print_toots.assert_called_once_with(
        mock_mastodon, favourite_toots, ctx_name="favourites", add_completion=False
    )


@patch("src.tootstream.toot.print_toots")
def test_bookmarks(mock_print_toots):
    mastodon = MagicMock()
    mastodon.bookmarks.return_value = "bookmarked_toots"
    rest = MagicMock()

    bookmarks(mastodon, rest)

    mock_print_toots.assert_called_once_with(
        mastodon, "bookmarked_toots", ctx_name="bookmarks", add_completion=False
    )


def test_about(mocker):
    mastodon_mock = mocker.Mock()
    mastodon_mock.api_base_url = "test_url"

    rest_mock = mocker.Mock()

    mocker.patch("builtins.print")
    mocker.patch("src.tootstream.toot.version", return_value="1.0.0")
    mocker.patch("src.tootstream.toot.cprint")
    mocker.patch("src.tootstream.toot.fg", return_value="")
    mocker.patch("src.tootstream.toot.attr", return_value="")

    from src.tootstream.toot import about

    about(mastodon_mock, rest_mock)

    builtins.print.assert_called_with("You are connected to ", end="")
    src.tootstream.toot.cprint.assert_called_with("test_url", "" + "")
    src.tootstream.toot.fg.assert_called_with("green")
    src.tootstream.toot.attr.assert_called_with("bold")


def test_lists_support_false(mocker):
    mocker.patch("src.tootstream.toot.list_support", return_value=False)
    mocker.patch("src.tootstream.toot.cprint")

    mastodon_mock = mocker.MagicMock()
    rest_mock = mocker.MagicMock()

    assert lists(mastodon_mock, rest_mock) is None
    src.tootstream.toot.list_support.assert_called_once_with(mastodon_mock)
    src.tootstream.toot.cprint.assert_not_called()


def test_lists_no_lists(mocker):
    mocker.patch("src.tootstream.toot.list_support", return_value=True)
    mocker.patch("src.tootstream.toot.cprint")

    mastodon_mock = mocker.MagicMock()
    mastodon_mock.lists.return_value = []

    rest_mock = mocker.MagicMock()

    assert lists(mastodon_mock, rest_mock) is None
    src.tootstream.toot.list_support.assert_called_once_with(mastodon_mock)
    src.tootstream.toot.cprint.assert_called_once_with(
        "No lists found", src.tootstream.toot.fg("red")
    )


def test_lists_with_lists(mocker):
    mocker.patch("src.tootstream.toot.list_support", return_value=True)
    mocker.patch("src.tootstream.toot.cprint")
    mocker.patch("src.tootstream.toot.printList")

    test_lists = ["list1", "list2"]
    mastodon_mock = mocker.MagicMock()
    mastodon_mock.lists.return_value = test_lists

    rest_mock = mocker.MagicMock()

    assert lists(mastodon_mock, rest_mock) is None
    src.tootstream.toot.list_support.assert_called_once_with(mastodon_mock)
    src.tootstream.toot.printList.assert_has_calls(
        mocker.call(list_item) for list_item in test_lists
    )


def test_listcreate(mocker):
    # create a mock for mastodon object and its methods
    mock_mastodon = mocker.Mock()
    mock_list_support = mocker.patch(
        "src.tootstream.toot.list_support", return_value=True
    )
    mock_cprint = mocker.patch("src.tootstream.toot.cprint")

    # starting the test
    rest = "TestList"
    listcreate(mock_mastodon, rest)

    # checking if the required functions were called correctly
    mock_list_support.assert_called_once_with(mock_mastodon)
    mock_mastodon.list_create.assert_called_once_with(rest)
    mock_cprint.assert_called_once_with(f"List {rest} created.", fg("green"))


@patch("src.tootstream.toot.list_support")
@patch("src.tootstream.toot.cprint")
@patch("src.tootstream.toot.get_list_id")
def test_listrename_not_supported(
    mock_get_list_id, mock_cprint, mock_list_support, mastodon, rest
):
    mock_list_support.return_value = False
    assert listrename(mastodon, rest) is None
    mock_list_support.assert_called_once_with(mastodon)


@patch("src.tootstream.toot.list_support")
@patch("src.tootstream.toot.cprint")
@patch("src.tootstream.toot.get_list_id")
def test_listrename_no_arguments(
    mock_get_list_id, mock_cprint, mock_list_support, mastodon, rest
):
    mock_list_support.return_value = True
    assert listrename(mastodon, "  ") is None
    mock_cprint.assert_called_once_with("Argument required.", fg("red"))


@patch("src.tootstream.toot.list_support")
@patch("src.tootstream.toot.cprint")
@patch("src.tootstream.toot.get_list_id")
def test_listrename_single_argument(
    mock_get_list_id, mock_cprint, mock_list_support, mastodon, rest
):
    mock_list_support.return_value = True
    assert listrename(mastodon, "test") is None
    mock_cprint.assert_called_once_with("Not enough arguments.", fg("red"))


@patch("src.tootstream.toot.list_support")
@patch("src.tootstream.toot.cprint")
@patch("src.tootstream.toot.get_list_id")
def test_listrename_happy_path(
    mock_get_list_id, mock_cprint, mock_list_support, mastodon
):
    mock_list_support.return_value = True
    mock_get_list_id.return_value = 123
    listrename(mastodon, "oldname newname")
    mock_get_list_id.assert_called_once_with(mastodon, "oldname")
    mastodon.list_update.assert_called_once_with(123, "newname")
    mock_cprint.assert_called_once_with("Renamed newname to oldname.", fg("green"))


def test_listdestroy_success(mocker):
    mastodon = mocker.MagicMock()
    rest = "test_list"

    mocker.patch("src.tootstream.toot.list_support", return_value=True)
    get_list_id_mock = mocker.patch(
        "src.tootstream.toot.get_list_id", return_value=1234
    )

    listdestroy(mastodon, rest)

    get_list_id_mock.assert_called_once_with(mastodon, rest)
    mastodon.list_delete.assert_called_once_with(1234)


def test_listdestroy_prints_success_message(mocker, capsys):
    mastodon = mocker.MagicMock()
    rest = "test_list"

    mocker.patch("src.tootstream.toot.list_support", return_value=True)
    mocker.patch("src.tootstream.toot.get_list_id", return_value=1234)

    listdestroy(mastodon, rest)

    captured = capsys.readouterr()
    assert "List {} deleted.".format(rest) in captured.out


@patch("src.tootstream.toot.list_support")
@patch("src.tootstream.toot.get_list_id")
@patch("src.tootstream.toot.cprint")
def test_listaccounts_no_support(mock_cprint, mock_get_list_id, mock_list_support):
    """Tests the listaccounts function when list support is not available."""
    mastodon = Mock()
    rest = "test"

    mock_list_support.return_value = False
    response = listaccounts(mastodon, rest)

    assert response is None
    mock_cprint.assert_not_called()
    mock_get_list_id.assert_not_called()


def test_listadd_no_list_support(mocker):
    mastodon = mocker.Mock()
    mastodon.side_effect = Exception
    mocker.patch("src.tootstream.toot.list_support", return_value=False)
    assert listadd(mastodon, "") is None


def test_listadd_no_arguments(mocker):
    mastodon = mocker.Mock()
    mocker.patch("src.tootstream.toot.list_support", return_value=True)
    mocker.patch("src.tootstream.toot.cprint")
    listadd(mastodon, "")
    src.tootstream.toot.cprint.assert_called_once_with("Argument required.", fg("red"))


def test_listadd_not_enough_arguments(mocker):
    mastodon = mocker.Mock()
    mocker.patch("src.tootstream.toot.list_support", return_value=True)
    mocker.patch("src.tootstream.toot.cprint")
    listadd(mastodon, "listname")
    src.tootstream.toot.cprint.assert_called_once_with(
        "Not enough arguments.", fg("red")
    )


def test_listadd_success(mocker):
    mastodon = mocker.Mock()
    mocker.patch("src.tootstream.toot.list_support", return_value=True)
    mocker.patch("src.tootstream.toot.get_list_id", return_value=1)
    mocker.patch("src.tootstream.toot.get_unique_userid", return_value=2)
    mocker.patch("src.tootstream.toot.cprint")
    listadd(mastodon, "listname @user@instance.example.com")
    mastodon.list_accounts_add.assert_called_once_with(1, 2)
    src.tootstream.toot.cprint.assert_called_once_with(
        "Added @user@instance.example.com to list listname.", fg("green")
    )


@patch("src.tootstream.toot.list_support")
@patch("src.tootstream.toot.cprint")
@patch("src.tootstream.toot.get_list_id")
@patch("src.tootstream.toot.get_unique_userid")
@patch("src.tootstream.toot.fg")
def test_listremove_no_list_support(
    mock_fg, mock_get_unique_userid, mock_get_list_id, mock_cprint, mock_list_support
):
    mock_list_support.return_value = False
    listremove("mastodon", "rest")
    mock_cprint.assert_not_called()
    mock_get_list_id.assert_not_called()
    mock_get_unique_userid.assert_not_called()


@patch("src.tootstream.toot.list_support")
@patch("src.tootstream.toot.cprint")
@patch("src.tootstream.toot.get_list_id")
@patch("src.tootstream.toot.get_unique_userid")
@patch("src.tootstream.toot.fg")
def test_listremove_no_args(
    mock_fg, mock_get_unique_userid, mock_get_list_id, mock_cprint, mock_list_support
):
    mock_list_support.return_value = True
    listremove("mastodon", "")
    mock_cprint.assert_called_once_with("Argument required.", mock_fg("red"))


@patch("src.tootstream.toot.list_support")
@patch("src.tootstream.toot.cprint")
@patch("src.tootstream.toot.get_list_id")
@patch("src.tootstream.toot.get_unique_userid")
@patch("src.tootstream.toot.fg")
def test_listremove_not_enough_args(
    mock_fg, mock_get_unique_userid, mock_get_list_id, mock_cprint, mock_list_support
):
    mock_list_support.return_value = True
    listremove("mastodon", "one_arg")
    mock_cprint.assert_called_once_with("Not enough arguments.", mock_fg("red"))


@patch("src.tootstream.toot.list_support")
@patch("src.tootstream.toot.Mastodon")
@patch("src.tootstream.toot.cprint")
@patch("src.tootstream.toot.get_list_id")
@patch("src.tootstream.toot.get_unique_userid")
@patch("src.tootstream.toot.fg")
def test_listremove_valid_list_remove(
    mock_fg,
    mock_get_unique_userid,
    mock_get_list_id,
    mock_cprint,
    MockMastodon,
    mock_list_support,
):
    mock_list_support.return_value = True
    mock_get_list_id.return_value = "list_id"
    mock_get_unique_userid.return_value = "userid"
    mastodon = MockMastodon()
    listremove(mastodon, "list user@instance.example.com")
    mastodon.list_accounts_delete.assert_called_once_with("list_id", "userid")
    mock_cprint.assert_called_once_with(
        "Removed user@instance.example.com from list list.", mock_fg("green")
    )


def test_get_mastodon_no_config_file(mocker):
    mocker.patch("os.path.isfile", return_value=False)

    with pytest.raises(SystemExit):
        get_mastodon("instance", "configpath", "profile")


def test_get_mastodon_no_token(mocker):
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch("os.access", return_value=True)
    mocker.patch("src.tootstream.toot.parse_config")
    mocker.patch(
        "src.tootstream.toot.get_or_input_profile",
        return_value=("instance", "client_id", "client_secret", None),
    )

    with pytest.raises(SystemExit):
        get_mastodon("instance", "configpath", "profile")
