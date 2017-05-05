var $lang = jQuery('.compiler-select').on('change', function() {
    window.localStorage['CSchoolSite_DEFAULT_COMPILER'] = this.value
});
if (window.localStorage['CSchoolSite_DEFAULT_COMPILER'])
    $lang.val(window.localStorage['CSchoolSite_DEFAULT_COMPILER']);