var gulp = require('gulp');
var copy = require('gulp-copy');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var gutil = require('gulp-util');

gulp.task('vendor', function() {
    gulp.src('./node_modules/bootstrap/dist/css/*')
        .pipe(gulp.dest('./static/css'));
    gulp.src('./node_modules/bootstrap/dist/js/*')
        .pipe(gulp.dest('./static/js'));
    gulp.src('./node_modules/bootstrap/dist/fonts/*')
        .pipe(gulp.dest('./static/fonts'));
    gulp.src('./node_modules/jquery/dist/jquery*.js')
        .pipe(gulp.dest('./static/js'));
    gulp.src('./node_modules/jquery-ui-dist/*.css')
        .pipe(gulp.dest('./static/css'));
    gulp.src('./node_modules/jquery-ui-dist/*.js')
        .pipe(gulp.dest('./static/js'));
    gulp.src('./node_modules/jquery-ui-dist/images/*')
        .pipe(gulp.dest('./static/css/images'));

    gulp.src('./node_modules/datatables.net/js/jquery.dataTables.js')
        .pipe(gulp.dest('./static/js'));
    gulp.src('./node_modules/datatables.net-bs/js/dataTables.bootstrap.js')
        .pipe(gulp.dest('./static/js'));

    gulp.src('./node_modules/datatables.net-bs/css/dataTables.bootstrap.css')
        .pipe(gulp.dest('./static/css'));
});

gulp.task('scripts', function () {
    return gulp.src(['./static/js/jquery.dataTables.js', './static/js/dataTables.bootstrap.js'])
        .pipe(concat('datatables.min.js'))
        .pipe(uglify())
        .pipe(gulp.dest('./static/js'));
});
