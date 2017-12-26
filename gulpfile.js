var gulp = require('gulp');
var sass = require('gulp-sass');
var minifyCSS = require('gulp-csso');
var concat = require('gulp-concat-multi');
var minifyJS = require('gulp-uglify');
var zip = require('gulp-zip');
var rename = require('gulp-regex-rename');
var clean = require('gulp-clean');

gulp.task('css', function () {
    return gulp.src('./sass/**/*.scss')
        .pipe(sass())
        .pipe(minifyCSS())
        .pipe(gulp.dest('./dist/css'));
});

gulp.task('js', function () {
    return concat({
        'files.js': ['js/shared/**/*.js', 'js/files.js'],
        'docs.js': ['js/shared/**/*.js', 'js/docs.js']
    })
        .pipe(minifyJS())
        .pipe(gulp.dest('./dist/js'));
});

gulp.task('clean-temp', function () {
    return gulp.src('./dist/temp', {read: false}).pipe(clean());
});

gulp.task('bundle-files:copy-css', ['clean-temp', 'css'], function () {
    return gulp.src('./dist/css/website_*.css').pipe(rename(/website_([A-Za-z]+)/, 'styles_$1')).pipe(gulp.dest('./dist/temp/css'));
});

gulp.task('bundle-files:copy-js', ['clean-temp', 'js'], function () {
    return gulp.src('./dist/js/files.js').pipe(rename(/files/, 'merged')).pipe(gulp.dest('./dist/temp/js'));
});

gulp.task('bundle-files:copy-html', ['clean-temp'], function () {
    return gulp.src('./templates/*.html').pipe(gulp.dest('./dist/temp/templates'));
});

gulp.task('bundle-files', ['clean-temp', 'bundle-files:copy-css', 'bundle-files:copy-js', 'bundle-files:copy-html'], function () {
    return gulp.src('./dist/temp/**/*',
        {
            base: './dist/temp/'
        })
        .pipe(zip('files-bundle.zip'))
        .pipe(gulp.dest('./dist/'));
});

gulp.task('watch', function () {
    gulp.watch('./sass/**/*.scss', ['css']);
    gulp.watch('./js/**/*.js', ['js']);
});

gulp.task('default', ['css', 'js']);