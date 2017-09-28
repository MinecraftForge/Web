var gulp = require('gulp');
var sass = require('gulp-sass');
var minifyCSS = require('gulp-csso');
var concat = require('gulp-concat-multi');
var minifyJS = require('gulp-uglify');

gulp.task('css', function () {
    return gulp.src('./sass/**/*.scss')
        .pipe(sass())
        .pipe(minifyCSS())
        .pipe(gulp.dest('./dist/css'))
});

gulp.task('js', function () {
    return concat({
        'files.js': ['js/shared/**/*.js', 'js/files.js'],
        'docs.js': ['js/shared/**/*.js', 'js/docs.js']
    })
        .pipe(minifyJS())
        .pipe(gulp.dest('./dist/js'))
});

gulp.task('watch', function () {
    gulp.watch('./sass/**/*.scss', ['css']);
    gulp.watch('./js/**/*.js', ['js']);
});

gulp.task('default', ['css', 'js']);