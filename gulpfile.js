var gulp = require('gulp');
var sass = require('gulp-sass');
var minifyCSS = require('gulp-csso');
var concat = require('gulp-concat');
var rename = require('gulp-rename');
var minifyJS = require('gulp-uglify');

gulp.task('css', function () {
    return gulp.src('./sass/**/*.scss')
        .pipe(sass())
        .pipe(minifyCSS())
        .pipe(gulp.dest('./dist/css'))
});

gulp.task('js', function () {
    return gulp.src('./js/**/*.js')
        .pipe(concat('merged.js'))
        .pipe(gulp.dest('./dist/js'))
        .pipe(rename('merged.min.js'))
        .pipe(minifyJS())
        .pipe(gulp.dest('./dist/js'))
});

gulp.task('default', ['css', 'js']);