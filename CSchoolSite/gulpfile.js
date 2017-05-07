var gulp = require('gulp');
var copy = require('gulp-copy');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var gutil = require('gulp-util');
var cleanCSS = require('gulp-clean-css');
var runSequence = require('run-sequence');


gulp.task('build', function(callback) {
    runSequence(
        'copy_bootstrap_css',
        'copy_bootstrap_js',
        'copy_bootstrap_fonts',
        'copy_jquery_js',
        'copy_jqueryui_css',
        'copy_jqueryui_js',
        'copy_jqueryui_images',
        'copy_datatables_js',
        'copy_datatablesbs_js',
        'copy_datatablesbs_css',
        'merge_datatables',
        'default_all_js',
        'jqueryui_all_js',
        'jqueryui_onoff_all_css',
        'jqueryui_datepicker_all_js',
        'compiler_all_js',
        'datatables_all_js',
        'enrolled_all_js',
        'relatives_choice_all_js',
        'user_profile_all_js',
        'news_all_js',
        'default_all_css',
        'choose_group_all_css',
        'jqueryui_all_css',
        'user_profile_all_css',
        'relatives_choice_all_css',
    callback)
});


gulp.task('copy_bootstrap_css', function() {
    return gulp.src('./node_modules/bootstrap/dist/css/*')
        .pipe(gulp.dest('./static/css'));
});
gulp.task('copy_bootstrap_js', function() {
    return gulp.src('./node_modules/bootstrap/dist/js/*')
        .pipe(gulp.dest('./static/js'));
});
gulp.task('copy_bootstrap_fonts', function() {
    return gulp.src('./node_modules/bootstrap/dist/fonts/*')
        .pipe(gulp.dest('./static/fonts'));
});
gulp.task('copy_jquery_js', function() {
    return gulp.src('./node_modules/jquery/dist/jquery*.js')
        .pipe(gulp.dest('./static/js'));
});
gulp.task('copy_jqueryui_css', function() {
    return gulp.src('./node_modules/jquery-ui-dist/*.css')
        .pipe(gulp.dest('./static/css'));
});
gulp.task('copy_jqueryui_js', function() {
    return gulp.src('./node_modules/jquery-ui-dist/*.js')
        .pipe(gulp.dest('./static/js'));
});
gulp.task('copy_jqueryui_images', function() {
    return gulp.src('./node_modules/jquery-ui-dist/images/*')
        .pipe(gulp.dest('./static/css/images'));
});
gulp.task('copy_datatables_js', function() {
    return gulp.src('./node_modules/datatables.net/js/jquery.dataTables.js')
        .pipe(gulp.dest('./static/js'));
});
gulp.task('copy_datatablesbs_js', function() {
    return gulp.src('./node_modules/datatables.net-bs/js/dataTables.bootstrap.js')
        .pipe(gulp.dest('./static/js'));
});
gulp.task('copy_datatablesbs_css', function() {
    return gulp.src('./node_modules/datatables.net-bs/css/dataTables.bootstrap.css')
        .pipe(gulp.dest('./static/css'));
});

gulp.task('merge_datatables', function () {
    return gulp.src(['./static/js/jquery.dataTables.js', './static/js/dataTables.bootstrap.js'])
        .pipe(concat('datatables.min.js'))
        .pipe(uglify())
        .pipe(gulp.dest('./static/js'));
});
gulp.task('default_all_js', function () {
    return gulp.src(['./static/js/jquery.min.js', './static/js/bootstrap.min.js', './main/static/js/common.js'])
        .pipe(concat('default.all.js'))
        .pipe(uglify())
        .pipe(gulp.dest('./static/js'));
});
gulp.task('jqueryui_all_js', function () {
    return gulp.src(['./static/js/default.all.js', './static/js/jquery-ui.min.js'])
        .pipe(concat('jquery-ui.all.js'))
        .pipe(uglify())
        .pipe(gulp.dest('./static/js'));
});
gulp.task('jqueryui_datepicker_all_js', function () {
    return gulp.src(['./static/js/jquery-ui.all.js', './main/static/js/datepicker.js'])
        .pipe(concat('jquery-ui-datepicker.all.js'))
        .pipe(uglify())
        .pipe(gulp.dest('./static/js'));
});
gulp.task('compiler_all_js', function () {
    return gulp.src(['./static/js/default.all.js', './applications/static/js/compiler.js'])
        .pipe(concat('compiler.all.js'))
        .pipe(uglify())
        .pipe(gulp.dest('./static/js'));
});
gulp.task('datatables_all_js', function () {
    return gulp.src(['./static/js/default.all.js', './static/js/datatables.min.js'])
        .pipe(concat('datatables.all.js'))
        .pipe(uglify())
        .pipe(gulp.dest('./static/js'));
});
gulp.task('enrolled_all_js', function () {
    return gulp.src(['./static/js/datatables.all.js', './applications/static/js/enrolled.js'])
        .pipe(concat('enrolled.all.js'))
        .pipe(uglify())
        .pipe(gulp.dest('./static/js'));
});
gulp.task('relatives_choice_all_js', function () {
    return gulp.src(['./static/js/datatables.all.js', './userprofile/static/js/relatives_choice.js'])
        .pipe(concat('relatives_choice.all.js'))
        .pipe(uglify())
        .pipe(gulp.dest('./static/js'));
});
gulp.task('user_profile_all_js', function () {
    return gulp.src(['./static/js/datatables.all.js', './userprofile/static/js/user_profile.js'])
        .pipe(concat('user_profile.all.js'))
        .pipe(uglify())
        .pipe(gulp.dest('./static/js'));
});
gulp.task('news_all_js', function () {
    return gulp.src(['./static/js/default.all.js', './news/static/js/news.js'])
        .pipe(concat('news.all.js'))
        .pipe(uglify())
        .pipe(gulp.dest('./static/js'));
});
gulp.task('default_all_css', function () {
    return gulp.src(['./main/static/css/common.css', './static/css/bootstrap.min.css'])
        .pipe(cleanCSS({level: 2}))
        .pipe(concat('default.all.css'))
        .pipe(gulp.dest('./static/css'));
});
gulp.task('choose_group_all_css', function () {
    return gulp.src(['./static/css/default.all.css', './applications/static/css/choose_group.css'])
        .pipe(cleanCSS({level: 2}))
        .pipe(concat('choose_group.all.css'))
        .pipe(gulp.dest('./static/css'));
});
gulp.task('jqueryui_all_css', function () {
    return gulp.src(['./static/css/default.all.css', './static/css/jquery-ui.min.css'])
        .pipe(cleanCSS({level: 2}))
        .pipe(concat('jquery-ui.all.css'))
        .pipe(gulp.dest('./static/css'));
});
gulp.task('jqueryui_onoff_all_css', function () {
    return gulp.src(['./static/css/jquery-ui.all.css', './main/static/css/onoffswitch.css'])
        .pipe(cleanCSS({level: 2}))
        .pipe(concat('jquery-ui-onoff.all.css'))
        .pipe(gulp.dest('./static/css'));
});
gulp.task('user_profile_all_css', function () {
    return gulp.src(['./static/css/default.all.css', './userprofile/static/css/user_profile.css', './static/css/dataTables.bootstrap.css'])
        .pipe(cleanCSS({level: 2}))
        .pipe(concat('user_profile.all.css'))
        .pipe(gulp.dest('./static/css'));
});
gulp.task('relatives_choice_all_css', function () {
    return gulp.src(['./static/css/default.all.css', './userprofile/static/css/relatives_choice.css', './static/css/dataTables.bootstrap.css'])
        .pipe(cleanCSS({level: 2}))
        .pipe(concat('relatives_choice.all.css'))
        .pipe(gulp.dest('./static/css'));
});
