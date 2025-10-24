require 'minitest/autorun'
require 'pathname'

class CVTruncationTest < Minitest::Test
  REPO_ROOT = Pathname.new(__dir__).parent

  def test_archive_single_cv_renders_full_content
    path = REPO_ROOT.join('_includes', 'archive-single-cv.html')
    assert path.exist?, "Missing {path}"
    content = path.read
    assert_includes content, '{{ post.content | markdownify }}', 'archive-single-cv.html should render full content not excerpt'
  end

  def test_archive_scss_contains_override
    path = REPO_ROOT.join('_sass', '_archive.scss')
    assert path.exist?, "Missing {path}"
    scss = path.read
    assert_includes scss, '.archive__item-body', 'scss override missing selector'
    assert_includes scss, 'max-height: none !important;', 'scss override missing rule'
  end
end
