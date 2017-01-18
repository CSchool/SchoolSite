var gulp = require('gulp');

var copy = require('gulp-copy');

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

})
